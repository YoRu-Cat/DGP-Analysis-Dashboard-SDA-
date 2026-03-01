from __future__ import annotations

from typing import List, Dict, Any
from functools import reduce
import os
import json

import pandas as pd

from core.contracts import PipelineService


_INT_COERCIBLE = lambda v: isinstance(v, (int, float)) and not isinstance(v, bool) and v == int(v)

_coerce_year_keys = lambda record: dict(map(
    lambda kv: (int(kv[0]), kv[1]) if _INT_COERCIBLE(kv[0]) else
               (int(kv[0]), kv[1]) if isinstance(kv[0], str) and kv[0].isdigit() else
               (kv[0], kv[1]),
    record.items(),
))


def _df_to_records(df: pd.DataFrame) -> List[Dict[str, Any]]:
    year_cols = list(filter(lambda c: isinstance(c, int), df.columns))
    str_year_cols = list(filter(
        lambda c: isinstance(c, str) and c.isdigit(),
        df.columns,
    ))
    rename_map = dict(map(lambda c: (c, int(c)), str_year_cols))
    df_fixed = df.rename(columns=rename_map) if rename_map else df
    return list(map(
        lambda row: row[1].to_dict(),
        df_fixed.iterrows(),
    ))


class CsvReader:

    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_and_push(self, service: PipelineService) -> None:
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"CSV file not found: {self.file_path}")
        df = pd.read_csv(self.file_path)
        records = _df_to_records(df)
        service.execute(records)


class JsonReader:

    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_and_push(self, service: PipelineService) -> None:
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"JSON file not found: {self.file_path}")
        with open(self.file_path, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        records = list(map(_coerce_year_keys, raw))
        service.execute(records)


class ExcelReader:

    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_and_push(self, service: PipelineService) -> None:
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Excel file not found: {self.file_path}")
        df = pd.read_excel(self.file_path)
        records = _df_to_records(df)
        service.execute(records)
