"""Output-stage consumer definitions for the Phase 3 pipeline."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Dict, Any

from phase3.input_module import SENTINEL


@dataclass(frozen=True)
class OutputModuleConfig:
    """Output-stage runtime configuration."""

    refresh_interval_seconds: float


class OutputModule:
    """Consumes processed packets and emits output updates."""

    def __init__(self, config: OutputModuleConfig, runtime: Dict[str, Any]) -> None:
        """Stores output configuration and shared runtime state."""
        self.config = config
        self.runtime = runtime

    def _notify(self, payload: Dict[str, Any]) -> None:
        """Sends telemetry updates when an observer is configured."""
        observer = self.runtime.get("observer")
        if observer is None:
            return
        callback = getattr(observer, "on_telemetry_update", None)
        if callable(callback):
            callback(payload)

    def run(self) -> None:
        """Runs the output consumer loop."""
        queue = self.runtime.get("processed_queue")
        if queue is None:
            raise ValueError("runtime['processed_queue'] is required")

        worker_count = int(self.runtime.get("worker_count", 1))
        results = self.runtime.get("results")
        if results is None:
            results = []
            self.runtime["results"] = results

        state = self.runtime.get("state", self.runtime)
        refresh = float(self.config.refresh_interval_seconds)
        done_workers = 0
        consumed = 0
        last_packet = None

        while done_workers < worker_count:
            packet = queue.get()
            if packet is SENTINEL:
                done_workers += 1
                continue

            results.append(packet)
            consumed += 1
            last_packet = packet

            if refresh > 0:
                time.sleep(refresh)

            self._notify({
                "event": "output_update",
                "consumed": consumed,
                "last_packet": last_packet,
            })

        state["consumed"] = consumed
        state["last_packet"] = last_packet
        state["completed"] = True

        self._notify({
            "event": "output_complete",
            "consumed": consumed,
            "last_packet": last_packet,
        })
