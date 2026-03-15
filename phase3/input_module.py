"""Input-stage producer and schema mapping for the Phase 3 pipeline."""

from __future__ import annotations

import csv
import time
from dataclasses import dataclass
from multiprocessing import Queue
from pathlib import Path
from typing import Any, Dict, List, Optional


SENTINEL = None


_TYPE_CASTERS: Dict[str, Any] = {
    "string":  str,
    "integer": int,
    "float":   float,
}


@dataclass(frozen=True)
class ColumnSchema:
    """Column mapping descriptor."""

    source_name: str
    internal_mapping: str
    data_type: str


@dataclass(frozen=True)
class InputModuleConfig:
    """Input module configuration."""

    dataset_path: str
    input_delay_seconds: float
    columns: List[ColumnSchema]


def build_input_config(cfg: Dict[str, Any]) -> InputModuleConfig:
    """Builds InputModuleConfig from the raw configuration dictionary."""
    p3 = cfg.get("phase3", {})
    dynamics = p3.get("pipeline_dynamics", {})
    raw_columns = p3.get("schema_mapping", {}).get("columns", [])

    columns = [
        ColumnSchema(
            source_name=col["source_name"],
            internal_mapping=col["internal_mapping"],
            data_type=col["data_type"],
        )
        for col in raw_columns
    ]

    return InputModuleConfig(
        dataset_path=p3.get("dataset_path", ""),
        input_delay_seconds=float(dynamics.get("input_delay_seconds", 0.01)),
        columns=columns,
    )


class SchemaMapper:
    """Maps and casts raw CSV rows into standardized packets."""

    def __init__(self, columns: List[ColumnSchema]) -> None:
        self._columns = columns

    def map_row(self, raw_row: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Returns a mapped packet, or None when mapping/casting fails."""
        packet: Dict[str, Any] = {}
        for col in self._columns:
            raw_value = raw_row.get(col.source_name)
            if raw_value is None:
                return None
            caster = _TYPE_CASTERS.get(col.data_type, str)
            try:
                packet[col.internal_mapping] = caster(raw_value.strip())
            except (ValueError, TypeError):
                return None
        return packet


class InputModule:
    """Produces mapped packets from the dataset into the raw queue."""

    def __init__(
        self,
        config: InputModuleConfig,
        raw_queue: Queue,
        num_workers: int,
    ) -> None:
        self._config = config
        self._raw_queue = raw_queue
        self._num_workers = num_workers
        self._mapper = SchemaMapper(config.columns)

    def run(self) -> None:
        """Reads rows, maps packets, pushes queue items, and sends sentinels."""
        path = Path(self._config.dataset_path)
        if not path.exists():
            raise FileNotFoundError(f"Input dataset not found: {path}")

        with open(path, newline="", encoding="utf-8") as csv_file:
            reader = csv.DictReader(csv_file)
            for raw_row in reader:
                packet = self._mapper.map_row(raw_row)
                if packet is None:
                    continue
                self._raw_queue.put(packet)
                if self._config.input_delay_seconds > 0:
                    time.sleep(self._config.input_delay_seconds)

        for _ in range(self._num_workers):
            self._raw_queue.put(SENTINEL)

