from __future__ import annotations

from typing import (
    Protocol,
    List,
    Dict,
    Any,
    Optional,
    Tuple,
    runtime_checkable,
)


@runtime_checkable
class DataRecord(Protocol):

    @property
    def country_name(self) -> str: ...

    @property
    def continent(self) -> str: ...

    @property
    def gdp_values(self) -> Dict[int, float]: ...


@runtime_checkable
class DataSink(Protocol):

    def write(self, records: List[Dict[str, Any]], title: str = "") -> None: ...

    def write_chart(
        self,
        chart_type: str,
        data: Dict[str, Any],
        title: str = "",
        options: Optional[Dict[str, Any]] = None,
    ) -> None: ...

    def write_summary(self, summary: Dict[str, Any], title: str = "") -> None: ...


@runtime_checkable
class PipelineService(Protocol):

    def execute(self, raw_data: List[Dict[str, Any]]) -> None: ...

    def get_available_analyses(self) -> List[str]: ...

    def run_analysis(
        self,
        analysis_name: str,
        params: Dict[str, Any],
    ) -> Optional[List[Dict[str, Any]]]: ...
