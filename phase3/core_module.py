"""Core processing workers for the Phase 3 pipeline."""

from __future__ import annotations

import hashlib
import hmac
from collections import deque
from dataclasses import dataclass
from typing import Dict, Any, Optional

from phase3 import get_phase3_config


@dataclass(frozen=True)
class CoreModuleConfig:
    """Core worker configuration."""

    core_parallelism: int


class StatelessVerifier:
    """Verifies packet signatures with PBKDF2-HMAC-SHA256."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self._secret     = config.get("secret_key", "").encode("utf-8")
        self._iterations = int(config.get("iterations", 100000))

    def process(self, packet: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Returns the packet when valid, otherwise None."""
        metric = float(packet.get("metric_value", 0.0))
        claimed = str(packet.get("security_hash", ""))

        salt = f"{metric:.2f}".encode("utf-8")
        computed = hashlib.pbkdf2_hmac("sha256", self._secret, salt, self._iterations).hex()

        if not hmac.compare_digest(computed, claimed):
            return None
        return packet


class StatefulAggregator:
    """Computes a sliding-window average over verified packets."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self._window_size: int   = int(config.get("running_average_window_size", 10))
        self._window:      deque = deque()

    @staticmethod
    def _sliding_window_average(window: deque) -> float:
        """Returns the mean of the current window."""
        return sum(window) / len(window)

    def process(self, packet: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Adds packet value to the window and attaches computed_metric."""
        val = float(packet.get("metric_value", 0.0))
        self._window.append(val)
        if len(self._window) > self._window_size:
            self._window.popleft()
        avg = self._sliding_window_average(self._window)
        return {**packet, "computed_metric": round(avg, 4)}
