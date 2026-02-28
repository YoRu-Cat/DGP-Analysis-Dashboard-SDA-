"""
Core Contracts Module — The Authority
======================================
Defines the Protocols (structural interfaces) that govern
how data flows through the system via Dependency Inversion.

Ownership: The Core module is the sole authority over these contracts.
Input and Output modules must satisfy these signatures to be "plugged in."

Protocols used:
    - DataSink      : Outbound abstraction — Core calls this to emit results.
    - PipelineService: Inbound abstraction  — Input calls this to push raw data.
    - DataRecord    : Structural type describing a single GDP record.

All contracts use typing.Protocol for structural (duck) typing, meaning any
class that implements the matching method signatures is automatically compatible
— no inheritance required.
"""

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


# ---------------------------------------------------------------------------
# Data Record — structural type for a single row of GDP data
# ---------------------------------------------------------------------------
@runtime_checkable
class DataRecord(Protocol):
    """
    Structural contract for a single GDP data record.
    Any dict-like object with these keys satisfies it at runtime.
    """

    @property
    def country_name(self) -> str: ...

    @property
    def continent(self) -> str: ...

    @property
    def gdp_values(self) -> Dict[int, float]: ...


# ---------------------------------------------------------------------------
# DataSink — Outbound Abstraction (owned by Core, implemented by Output)
# ---------------------------------------------------------------------------
@runtime_checkable
class DataSink(Protocol):
    """
    Outbound Abstraction — the Core calls this to emit processed results.

    Any Output module (ConsoleWriter, GraphicsChartWriter, FileWriter, …)
    must implement **all** methods below to satisfy the contract.

    The Core NEVER imports a concrete writer — it only depends on this Protocol.
    """

    def write(self, records: List[Dict[str, Any]], title: str = "") -> None:
        """
        Write a generic list of result records.

        Parameters
        ----------
        records : list[dict]
            Each dict represents one result row (keys vary by analysis).
        title : str, optional
            Human-readable title for the output section.
        """
        ...

    def write_chart(
        self,
        chart_type: str,
        data: Dict[str, Any],
        title: str = "",
        options: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Emit a visualisation / chart.

        Parameters
        ----------
        chart_type : str
            One of: 'bar', 'line', 'pie', 'grouped_bar', 'heatmap'.
        data : dict
            Payload understood by the concrete writer.
            Typically ``{"labels": [...], "values": [...], ...}``.
        title : str
            Chart heading.
        options : dict, optional
            Extra rendering hints (colours, sizes, …).
        """
        ...

    def write_summary(self, summary: Dict[str, Any], title: str = "") -> None:
        """
        Emit a textual summary / statistical block.

        Parameters
        ----------
        summary : dict
            Key-value pairs to display.
        title : str
            Section heading.
        """
        ...


# ---------------------------------------------------------------------------
# PipelineService — Inbound Abstraction (owned by Core, called by Input)
# ---------------------------------------------------------------------------
@runtime_checkable
class PipelineService(Protocol):
    """
    Inbound Abstraction — the Input module calls this to push raw data
    into the Core for processing.

    The Input module is "blind" to the Core's internal logic; it only
    knows this protocol shape.
    """

    def execute(self, raw_data: List[Dict[str, Any]]) -> None:
        """
        Accept raw data rows and run the full analysis pipeline.

        Parameters
        ----------
        raw_data : list[dict]
            Each dict has at minimum:
                - 'Country Name' : str
                - 'Continent'    : str
                - year (int) keys mapping to GDP float values
        """
        ...

    def get_available_analyses(self) -> List[str]:
        """Return the list of analysis names the engine can perform."""
        ...

    def run_analysis(
        self,
        analysis_name: str,
        params: Dict[str, Any],
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Run a single named analysis with the given parameters.

        Parameters
        ----------
        analysis_name : str
            Key identifying the analysis (e.g. 'top_countries', 'growth_rate').
        params : dict
            Analysis-specific parameters (continent, year, date_range, n …).

        Returns
        -------
        list[dict] | None
            Result rows, or None if the analysis is not applicable.
        """
        ...
