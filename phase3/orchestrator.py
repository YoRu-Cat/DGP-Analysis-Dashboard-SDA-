from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class OrchestratorConfig:
    """Configuration placeholder for process orchestration behavior."""

    raw_queue_max_size: int
    processed_queue_max_size: int


class PipelineOrchestrator:
    """Main process coordinator for producer, workers, aggregator, and output."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config

    def run(self) -> None:
        """Creates queues and process workers, then starts pipeline execution."""
        raise NotImplementedError("PipelineOrchestrator.run will be implemented in Part 10")
