from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional


@dataclass(frozen=True)
class CoreModuleConfig:
    """Configuration placeholder for the generic core workers."""

    core_parallelism: int


class StatelessVerifier:
    """Stateless worker stage placeholder for signature verification."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    def process(self, packet: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validates packet authentication and either emits or drops it."""
        raise NotImplementedError("StatelessVerifier.process will be implemented in Part 4")


class StatefulAggregator:
    """Stateful worker stage placeholder for stream ordering and sliding average."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    def process(self, packet: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Aggregates verified stream and computes stateful metrics."""
        raise NotImplementedError("StatefulAggregator.process will be implemented in Part 5")
