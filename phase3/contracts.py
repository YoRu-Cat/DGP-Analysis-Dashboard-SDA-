from __future__ import annotations

from typing import Protocol, Dict, Any, Optional, runtime_checkable


@runtime_checkable
class GenericInputModule(Protocol):
    """Reads source rows and emits standardized packets."""

    def run(self) -> None: ...


@runtime_checkable
class GenericCoreModule(Protocol):
    """Consumes standardized packets and emits processed packets."""

    def run(self) -> None: ...


@runtime_checkable
class GenericOutputModule(Protocol):
    """Consumes processed packets and updates observers or sinks."""

    def run(self) -> None: ...


@runtime_checkable
class TelemetryObserver(Protocol):
    """Observer contract for queue telemetry updates."""

    def on_telemetry_update(self, snapshot: Dict[str, Any]) -> None: ...


@runtime_checkable
class PipelineTelemetrySubject(Protocol):
    """Subject contract for telemetry monitoring and subscription."""

    def subscribe(self, observer: TelemetryObserver) -> None: ...

    def unsubscribe(self, observer: TelemetryObserver) -> None: ...

    def poll_once(self) -> Dict[str, Any]: ...


@runtime_checkable
class PacketProcessor(Protocol):
    """Functional processor contract for packet transformation."""

    def process(self, packet: Dict[str, Any]) -> Optional[Dict[str, Any]]: ...
