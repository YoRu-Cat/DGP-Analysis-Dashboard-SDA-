from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

from phase3.contracts import TelemetryObserver


@dataclass(frozen=True)
class TelemetryThresholds:
    """Queue utilization thresholds used to classify stream health."""

    flowing_max: float = 0.50
    warning_max: float = 0.85


class PipelineTelemetry:
    """Observer subject placeholder for queue backpressure monitoring."""

    def __init__(self, queues: Dict[str, Any], thresholds: TelemetryThresholds | None = None) -> None:
        self.queues = queues
        self.thresholds = thresholds or TelemetryThresholds()
        self._observers: List[TelemetryObserver] = []

    def subscribe(self, observer: TelemetryObserver) -> None:
        self._observers.append(observer)

    def unsubscribe(self, observer: TelemetryObserver) -> None:
        self._observers = [obs for obs in self._observers if obs is not observer]

    def poll_once(self) -> Dict[str, Any]:
        """Collects queue telemetry snapshot for publication."""
        raise NotImplementedError("PipelineTelemetry.poll_once will be implemented in Part 7")

    def publish(self, snapshot: Dict[str, Any]) -> None:
        for observer in self._observers:
            observer.on_telemetry_update(snapshot)
