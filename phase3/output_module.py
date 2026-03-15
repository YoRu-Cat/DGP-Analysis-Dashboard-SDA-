from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class OutputModuleConfig:
    """Configuration placeholder for dynamic output rendering."""

    refresh_interval_seconds: float


class OutputModule:
    """Base shell for observer-driven output module implementation."""

    def __init__(self, config: OutputModuleConfig, runtime: Dict[str, Any]) -> None:
        self.config = config
        self.runtime = runtime

    def run(self) -> None:
        """Entry point for output consumer process."""
        raise NotImplementedError("OutputModule.run will be implemented in Part 8")
