"""Output-stage consumer definitions for the Phase 3 pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


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

    def run(self) -> None:
        """Runs the output consumer loop."""
        raise NotImplementedError("OutputModule.run will be implemented in Part 8")
