"""Queue telemetry publisher for the Phase 3 pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any

from phase3.contracts import TelemetryObserver


@dataclass(frozen=True)
class TelemetryThresholds:
    """Queue utilization thresholds for health classification."""

    flowing_max: float = 0.50
    warning_max: float = 0.85


class PipelineTelemetry:
    """Publishes queue backpressure telemetry to observers."""

    def __init__(self, queues: Dict[str, Any], thresholds: TelemetryThresholds | None = None) -> None:
        """Initializes queue handles, thresholds, and observer collection."""
        self.queues = queues
        self.thresholds = thresholds or TelemetryThresholds()
        self._observers: List[TelemetryObserver] = []

    def subscribe(self, observer: TelemetryObserver) -> None:
        """Registers an observer for telemetry updates."""
        self._observers.append(observer)

    def unsubscribe(self, observer: TelemetryObserver) -> None:
        """Removes a previously registered observer."""
        self._observers = [obs for obs in self._observers if obs is not observer]

    def _classify(self, utilization: float) -> str:
        """Classifies utilization into flowing, warning, or critical."""
        if utilization < self.thresholds.flowing_max:
            return "flowing"
        if utilization < self.thresholds.warning_max:
            return "warning"
        return "critical"

    @staticmethod
    def _queue_size(queue: Any) -> int:
        """Returns queue size when available, otherwise 0."""
        try:
            return int(queue.qsize())
        except Exception:
            return 0

    @staticmethod
    def _queue_capacity(queue: Any) -> int:
        """Returns queue capacity when known, otherwise 0."""
        maxsize = int(getattr(queue, "_maxsize", getattr(queue, "maxsize", 0)) or 0)
        return max(0, maxsize)

    def poll_once(self) -> Dict[str, Any]:
        """Collects one telemetry snapshot for publication."""
        queues_snapshot: Dict[str, Dict[str, Any]] = {}

        for queue_name, queue in self.queues.items():
            size = self._queue_size(queue)
            capacity = self._queue_capacity(queue)
            utilization = (size / capacity) if capacity > 0 else 0.0
            state = self._classify(utilization)

            queues_snapshot[queue_name] = {
                "size": size,
                "capacity": capacity,
                "utilization": round(utilization, 4),
                "state": state,
            }

        if not queues_snapshot:
            overall_state = "flowing"
        else:
            state_rank = {"flowing": 0, "warning": 1, "critical": 2}
            overall_state = max(
                (entry["state"] for entry in queues_snapshot.values()),
                key=lambda s: state_rank.get(s, 0),
            )

        snapshot = {
            "queues": queues_snapshot,
            "overall_state": overall_state,
            "thresholds": {
                "flowing_max": self.thresholds.flowing_max,
                "warning_max": self.thresholds.warning_max,
            },
        }

        self.publish(snapshot)
        return snapshot

    def publish(self, snapshot: Dict[str, Any]) -> None:
        """Pushes a snapshot to all registered observers."""
        for observer in self._observers:
            observer.on_telemetry_update(snapshot)
