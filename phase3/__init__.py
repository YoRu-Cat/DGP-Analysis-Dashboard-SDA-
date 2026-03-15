"""Phase 3 generic concurrent pipeline package."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


def get_phase3_config(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """Returns the Phase 3 config block from nested or flat config layouts."""
    if "phase3" in cfg and isinstance(cfg["phase3"], dict):
        return cfg["phase3"]

    phase3_keys = {
        "dataset_path",
        "pipeline_dynamics",
        "schema_mapping",
        "processing",
        "visualizations",
    }
    if any(key in cfg for key in phase3_keys):
        return cfg
    return {}


def resolve_dataset_path(dataset_path: str) -> Path:
    """Resolves the configured dataset path relative to the project root."""
    path = Path(dataset_path)
    if path.is_absolute():
        return path
    project_root = Path(__file__).resolve().parent.parent
    return (project_root / path).resolve()
