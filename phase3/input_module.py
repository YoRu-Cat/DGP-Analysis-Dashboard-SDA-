from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class InputModuleConfig:
    """Configuration placeholder for the generic input module."""

    dataset_path: str
    input_delay_seconds: float


class InputModule:
    """Base shell for schema-driven producer implementation."""

    def __init__(self, config: InputModuleConfig, runtime: Dict[str, Any]) -> None:
        self.config = config
        self.runtime = runtime

    def run(self) -> None:
        """Entry point for input producer process."""
        raise NotImplementedError("InputModule.run will be implemented in Part 3")
