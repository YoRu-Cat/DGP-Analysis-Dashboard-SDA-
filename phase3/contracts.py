"""Protocol contracts for the Phase 3 pipeline components."""

from __future__ import annotations

from typing import Protocol, Dict, Any, Optional, runtime_checkable


@runtime_checkable
class GenericInputModule(Protocol):
    """Produces standardized packets from an input source."""

    def run(self) -> None: ...


@runtime_checkable
class GenericCoreModule(Protocol):
    """Processes standardized packets into downstream packets."""

    def run(self) -> None: ...


@runtime_checkable
class GenericOutputModule(Protocol):
    """Consumes processed packets and writes output updates."""

    def run(self) -> None: ...


@runtime_checkable
class TelemetryObserver(Protocol):
    """Receives telemetry snapshot updates."""

    def on_telemetry_update(self, snapshot: Dict[str, Any]) -> None: ...


@runtime_checkable
class PipelineTelemetrySubject(Protocol):
    """Publishes queue telemetry to subscribed observers."""

    def subscribe(self, observer: TelemetryObserver) -> None: ...

    def unsubscribe(self, observer: TelemetryObserver) -> None: ...

    def poll_once(self) -> Dict[str, Any]: ...


@runtime_checkable
class PacketProcessor(Protocol):
    """Transforms one packet and may drop invalid packets."""

    def process(self, packet: Dict[str, Any]) -> Optional[Dict[str, Any]]: ...
