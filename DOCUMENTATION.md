# GDP Analysis Dashboard — Complete Project Documentation

**Project**: GDP Analysis Dashboard  
**Author**: YoRu-Cat  
**Repository**: [DGP-Analysis-Dashboard-SDA-](https://github.com/YoRu-Cat/DGP-Analysis-Dashboard-SDA-)  
**Date**: March 2026  
**Python**: 3.14.3  
**Version**: 2.0

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [How to Run](#2-how-to-run)
3. [Project Structure](#3-project-structure)
4. [Architecture Overview](#4-architecture-overview)
5. [Phase 1 — Interactive GUI Dashboard](#5-phase-1--interactive-gui-dashboard)
   - 5.1 [Dashboard Layout & Theme](#51-dashboard-layout--theme)
   - 5.2 [All 11 Phase 1 Analyses](#52-all-11-phase-1-analyses)
   - 5.3 [Data Loader Module](#53-data-loader-module)
   - 5.4 [Data Processor Module](#54-data-processor-module)
   - 5.5 [Dashboard Controls & Interaction](#55-dashboard-controls--interaction)
6. [Phase 2 — Modular Orchestration & Dependency Inversion](#6-phase-2--modular-orchestration--dependency-inversion)
   - 6.1 [Objective](#61-objective)
   - 6.2 [The Golden Rules — DIP Compliance](#62-the-golden-rules--dip-compliance)
   - 6.3 [Core Module — The Domain](#63-core-module--the-domain)
   - 6.4 [Input Module — The Source](#64-input-module--the-source)
   - 6.5 [Output Module — The Sink](#65-output-module--the-sink)
   - 6.6 [Main Module — The Orchestrator](#66-main-module--the-orchestrator)
   - 6.7 [All 8 Phase 2 Analyses](#67-all-8-phase-2-analyses)
   - 6.8 [GUI Integration of Phase 2](#68-gui-integration-of-phase-2)
7. [Configuration System — config.json](#7-configuration-system--configjson)
8. [Data Flow — End-to-End Workflows](#8-data-flow--end-to-end-workflows)
9. [Functional Programming Compliance](#9-functional-programming-compliance)
10. [Data-Driven Programming](#10-data-driven-programming)
11. [PlantUML Architecture Diagram](#11-plantuml-architecture-diagram)
12. [Testing](#12-testing)
13. [Dependencies](#13-dependencies)
14. [Deliverables Checklist](#14-deliverables-checklist)
15. [Standard Library Tools Used](#15-standard-library-tools-used)
16. [Troubleshooting](#16-troubleshooting)

---

## 1. Project Overview

The GDP Analysis Dashboard is a full-featured data analysis application built in Python that visualizes and analyzes GDP data for 266 countries spanning 65 years (1960–2024). The project is developed in two phases:

- **Phase 1**: A monolithic interactive GUI dashboard with 11 analysis types, built with tkinter/ttkbootstrap and matplotlib. It follows strict functional programming conventions (zero `for`/`while` loops) and reads all behavior from `config.json`.

- **Phase 2**: A modular architecture refactoring that decouples business logic from data ingestion and presentation using the **Dependency Inversion Principle (DIP)**. The Core defines `typing.Protocol` contracts; Input and Output plugins satisfy these contracts; an Orchestrator (`main.py`) wires everything at runtime using `importlib` and a config-driven factory.

Both phases coexist in the final application. The GUI dashboard includes all 11 Phase 1 analyses plus 9 Phase 2 engine analyses selectable via radio buttons.

**Key facts:**

- 266 countries/regions, 65 year columns (1960–2024), ~84% data coverage
- 20 total analysis types (11 Phase 1 + 8 Phase 2 + Run All)
- 3 Protocol contracts, 3 input plugins, 3 output plugins
- Zero `for`/`while` loops in the entire codebase
- Single entry point: `python main.py` (GUI default, CLI available)
- X/Twitter professional dark theme (pure black backgrounds, `#e7e9ea` text, `#1d9bf0` accents)

---

## 2. How to Run

### Prerequisites

- Python 3.10+ (developed and tested on 3.14.3)
- `gdp_with_continent_filled.xlsx` in the `proj/` directory

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Launch

| Command                        | What it does                                 |
| ------------------------------ | -------------------------------------------- |
| `python main.py`               | Launch the GUI dashboard (default)           |
| `python main.py --gui`         | Launch the GUI dashboard (explicit)          |
| `python main.py --cli`         | Run all 8 Phase 2 analyses in the console    |
| `python main.py top_countries` | Run a single Phase 2 analysis in the console |
| `python main.py --list`        | List all available Phase 2 analysis names    |
| `python main.py --help`        | Show usage information                       |

Or double-click `launch_dashboard.bat` on Windows.

### Run Tests

```bash
python test_dashboard.py
```

Expected: 8/8 tests passed.

---

## 3. Project Structure

```
proj/
├── main.py                        # Entry point — Orchestrator (GUI + CLI)
├── config.json                    # All runtime configuration
├── architecture.puml              # PlantUML architecture diagram
├── gdp_dashboard_refactored.py    # GUI dashboard (Phase 1 + Phase 2 integrated)
├── data_loader.py                 # ConfigLoader, GDPDataLoader (Phase 1)
├── data_processor.py              # GDPDataProcessor — statistics, filtering (Phase 1)
├── test_dashboard.py              # Automated test suite (8 tests)
├── requirements.txt               # Python dependencies
├── launch_dashboard.bat           # Windows launcher script
├── gdp_with_continent_filled.xlsx # GDP dataset (266 countries, 1960–2024)
├── README.md                      # Quick-start documentation
├── DOCUMENTATION.md               # This file — complete project documentation
│
├── core/                          # THE DOMAIN — owns all contracts (Phase 2)
│   ├── __init__.py                # Re-exports: DataSink, PipelineService, DataRecord
│   ├── contracts.py               # 3 Protocol definitions (structural interfaces)
│   └── engine.py                  # TransformationEngine — 8 analyses, DI of DataSink
│
├── plugins/                       # INPUT & OUTPUT implementations (Phase 2)
│   ├── __init__.py                # Package exports
│   ├── inputs.py                  # CsvReader, JsonReader, ExcelReader
│   └── outputs.py                 # ConsoleWriter, GraphicsChartWriter, TkinterSink
│
└── data/                          # Source files directory
    └── __init__.py                # Package marker
```

### File Sizes (approximate)

| File                          | Lines | Role                                           |
| ----------------------------- | ----- | ---------------------------------------------- |
| `gdp_dashboard_refactored.py` | ~1801 | GUI dashboard — all visualization and UI logic |
| `core/engine.py`              | ~338  | Business logic — 8 analysis transformations    |
| `plugins/outputs.py`          | ~470  | 3 output sink implementations                  |
| `data_processor.py`           | ~226  | Phase 1 statistical calculations               |
| `data_loader.py`              | ~169  | Config loading and data loading                |
| `test_dashboard.py`           | ~247  | 8 automated tests                              |
| `main.py`                     | ~140  | Orchestrator — CLI + GUI entry point           |
| `config.json`                 | ~243  | Full runtime configuration                     |
| `plugins/inputs.py`           | ~78   | 3 input reader implementations                 |
| `core/contracts.py`           | ~55   | 3 Protocol definitions                         |
| `architecture.puml`           | ~193  | PlantUML diagram                               |

---

## 4. Architecture Overview

The system has two architectural layers that work together:

### Phase 1 Architecture (GUI Layer)

```
config.json → ConfigLoader → GDPDataLoader → GDPDataProcessor → GDPDashboard
                                                                      │
                                                                 matplotlib
                                                                 tkinter/ttkbootstrap
```

- `ConfigLoader` reads and validates `config.json`
- `GDPDataLoader` loads the Excel/CSV data, validates columns, extracts metadata
- `GDPDataProcessor` provides statistical calculations (growth rates, correlations, comparisons)
- `GDPDashboard` is the tkinter application with 11 analysis views

### Phase 2 Architecture (Modular DIP Layer)

```
┌─────────────────────────────────────────────────────────────────────┐
│                      main.py (Orchestrator)                         │
│  - Parses config.json                                               │
│  - Dictionary-based Factory (importlib.import_module)               │
│  - Dependency Injection: wires sink → engine → reader               │
└─────────────┬────────────────────┬──────────────────┬───────────────┘
              │                    │                  │
              ▼                    ▼                  ▼
   ┌──────────────────┐  ┌─────────────────┐  ┌──────────────────────┐
   │ plugins/inputs.py│  │ core/            │  │ plugins/outputs.py   │
   │                  │  │ contracts.py     │  │                      │
   │ CsvReader     ───┼─▶│ PipelineService  │  │ ConsoleWriter     ◀──│
   │ JsonReader       │  │ (Protocol)       │  │ GraphicsChartWriter  │
   │ ExcelReader      │  │                  │  │ TkinterSink          │
   └──────────────────┘  │ engine.py        │  └──────────────────────┘
                         │ TransformEngine──┼─▶ DataSink (Protocol)
                         └─────────────────┘
```

**All dependency arrows point toward Core.** Plugins depend on Core's protocols; Core never imports plugins.

### Combined Architecture (GUI + Engine)

When running the GUI, both layers merge:

```
GDPDashboard
  ├── Phase 1: GDPDataProcessor → matplotlib charts (11 analyses)
  └── Phase 2: TransformationEngine → TkinterSink → renders in same GUI (8 analyses)
```

The `TkinterSink` output plugin is bound to the dashboard's visualization and statistics frames, so Phase 2 engine results render directly in the GUI alongside Phase 1 analyses.

---

## 5. Phase 1 — Interactive GUI Dashboard

### 5.1 Dashboard Layout & Theme

The dashboard uses **ttkbootstrap** with the `"darkly"` base theme, overridden to achieve an X/Twitter professional dark aesthetic:

- **Background**: Pure black `#000000` / `#0a0a0a`
- **Text primary**: `#e7e9ea` (near-white)
- **Text secondary**: `#71767b` (grey)
- **Accent**: `#1d9bf0` (Twitter blue)
- **Borders**: `#2f3336` (subtle dark grey)
- **Buttons**: White `#ffffff` with black `#000000` text
- **Font**: Segoe UI throughout, Cascadia Code for statistics text

#### Layout Structure

```
┌──────────────────────────────────────────────────────────────────┐
│  🌍 GDP Analysis Dashboard 📊         (Title Bar + accent line) │
├──────────────┬───────────────────────────────────────────────────┤
│  LEFT PANEL  │  RIGHT PANEL                                     │
│  (350px)     │                                                   │
│              │  ┌─────────────────────────────────────────────┐  │
│ 📈 Analysis  │  │  📊 Visualization  │  📋 Statistics         │  │
│   Type       │  │                    │                        │  │
│ (20 radios)  │  │  matplotlib chart  │  ScrolledText with    │  │
│              │  │  rendered via       │  formatted analysis   │  │
│ 🌐 Country   │  │  FigureCanvasTkAgg │  results              │  │
│   Selection  │  │                    │                        │  │
│              │  └─────────────────────────────────────────────┘  │
│ 🗺️ Continent │                                                   │
│              │                                                   │
│ 📅 Year Range│                                                   │
│              │                                                   │
│ 🏆 Top N     │                                                   │
│              │                                                   │
│ ⚡ Actions    │                                                   │
│  [Analyze]   │                                                   │
│  [Export]     │                                                   │
│  [Clear]     │                                                   │
└──────────────┴───────────────────────────────────────────────────┘
```

**Left panel controls:**

- **Analysis Type**: 20 radio buttons (11 Phase 1 + separator + 8 Phase 2 + Run All)
- **Country Selection**: Primary country dropdown + multi-select compare listbox
- **Continent Selection**: Dropdown filtered from data
- **Year Range**: From/To year combos
- **Top N**: Spinbox (5–50)
- **Actions**: Analyze, Export to TXT, Clear Visualization

**Right panel:**

- **Visualization tab**: matplotlib charts embedded via `FigureCanvasTkAgg`
- **Statistics tab**: `ScrolledText` widget with formatted text results

**Interactions:**

- Changing any control triggers `perform_analysis_delayed()` with a 300ms debounce
- Changing primary country auto-switches to Country Trend analysis
- Selecting items in compare listbox auto-switches to Compare Countries
- All config defaults (region, country, year) loaded from `config.json`

### 5.2 All 11 Phase 1 Analyses

#### 1. Country GDP Trend (`country_trend`)

**Method**: `plot_country_trend()`  
**Input**: Primary country, year range  
**Chart**: Line plot with fill-between shading  
**Stats**: Country statistics — max, min, mean, growth rate, peak year

Shows GDP trajectory over time for a single country. Uses the cyberpunk glow effect. Y-axis formatted as `$T`/`$B`/`$M`.

#### 2. Compare Countries (`compare_countries`)

**Method**: `plot_compare_countries()`  
**Input**: Selected countries from compare listbox (up to 10), year range  
**Chart**: Multi-line plot with different colors from palette  
**Stats**: Comparison statistics — each country's latest GDP, growth, max, min

Allows side-by-side GDP comparison of multiple countries on one chart. Maximum 10 countries (configurable via `ui.max_compare_countries`).

#### 3. Continent Analysis (`continent_analysis`)

**Method**: `plot_continent_analysis()`  
**Input**: Selected continent, year range  
**Chart**: 4-panel subplot:

1. Total continent GDP trend (line)
2. Top 10 countries by latest year (horizontal bar)
3. Average GDP per country (line)
4. GDP distribution histogram
   **Stats**: Continent statistics — total GDP, country count, top/bottom performers

#### 4. Top Countries (`top_countries`)

**Method**: `plot_top_countries()`  
**Input**: Continent (or all), year, top N  
**Chart**: Horizontal bar chart with per-bar color cycling  
**Stats**: Top countries table with GDP values, ranks, and percentage of total

#### 5. GDP Growth Rate (`growth_rate`)

**Method**: `plot_growth_rate()`  
**Input**: Primary country, year range  
**Chart**: Bar chart — green bars for positive growth, red for negative  
**Stats**: Growth statistics — average annual growth, volatility, max growth/decline years

Calculates year-over-year percentage change using `GDPDataProcessor.calculate_growth_rates()`.

#### 6. Statistical Summary (`statistics`)

**Method**: `show_statistics()`  
**Input**: Primary country, continent, year range  
**Chart**: None (text-only in Statistics tab)  
**Stats**: Comprehensive statistical report:

- Country-level: max, min, mean, median, std dev, growth summary
- Continent-level: total GDP, avg per country, top 5, bottom 5
- World stats: global totals, averages, distributions
- Rankings by continent for latest year

#### 7. Year Comparison (`year_comparison`)

**Method**: `plot_year_comparison()`  
**Input**: Year range (auto-samples up to 6 years), continents  
**Chart**: Grouped bar chart — each continent grouped by sampled years  
**Stats**: Year comparison table — GDP per continent per year

Automatically samples comparison years across the range (max 6, configurable).

#### 8. Correlation Analysis (`correlation`)

**Method**: `plot_correlation()`  
**Input**: Primary country + compare listbox selections (up to 15)  
**Chart**: Seaborn heatmap with annotated correlation coefficients  
**Stats**: Top 10 highest/lowest correlations with values

Uses `GDPDataProcessor.get_correlation_matrix()` and `get_top_correlations()`. Default colormap: coolwarm.

#### 9. Regional Analysis — Pie + Bar (`phase1_regional`)

**Method**: `plot_phase1_regional_analysis()`  
**Input**: Year (latest from range), continents from `config.json`'s `phase1_operations.compute_regions`  
**Chart**: 2-panel:

1. Pie chart — continent GDP distribution
2. Bar chart — same data as bars
   **Stats**: Regional statistics table

Uses chart types specified in `phase1_visualizations.region_charts`.

#### 10. Year Analysis — Line + Scatter (`phase1_year`)

**Method**: `plot_phase1_year_analysis()`  
**Input**: Primary country, year range  
**Chart**: 2-panel:

1. Line chart — GDP trend
2. Scatter plot — GDP data points
   **Stats**: Country year-by-year data

Uses chart types specified in `phase1_visualizations.year_charts`.

#### 11. Complete Analysis — All Charts (`phase1_complete`)

**Method**: `plot_phase1_complete_analysis()`  
**Input**: Primary country, continent, year range  
**Chart**: 4-panel subplot:

1. Pie chart — continent distribution
2. Bar chart — continent totals
3. Line chart — country trend
4. Scatter plot — country data points
   **Stats**: Combined statistics for region + country

Has `enable_histogram` option from `phase1_visualizations` to optionally add a 5th panel.

### 5.3 Data Loader Module

**File**: `data_loader.py` (~169 lines)

#### ConfigLoader

```python
class ConfigLoader:
    def __init__(self, config_path='config.json'):
        self.config = self._load_config()

    def _load_config(self):    # Reads JSON, handles FileNotFoundError & decode errors
    def _validate_config(self): # Checks required sections: data, ui, colors, analysis_types, visualization
    def get(self, section, key=None): # Section/key accessor
```

- Opens `config.json` with `encoding='utf-8'` (required on Windows — avoids cp1252 errors)
- Validates that all required config sections exist
- Validates that `data` section has `file_path` and `required_columns`

#### GDPDataLoader

```python
class GDPDataLoader:
    def __init__(self, config):
    def load_data(self):        # Smart format detection (.csv / .xlsx / .xls)
    def _validate_data(self):   # Checks: non-empty, required columns, year columns exist
    def _extract_metadata(self): # Extracts: year_columns, countries, continents
    def get_dataframe(self):
    def get_year_columns(self):
    def get_countries(self):
    def get_continents(self):
    def get_summary(self):      # Returns dict: total_countries, total_years, year_range, continents
```

- Reads the file path from config's `data.file_path`
- Auto-detects format by extension (`.csv` → `pd.read_csv`, `.xlsx` → `pd.read_excel`)
- Validates `Country Name` and `Continent` columns exist
- Extracts sorted year columns (integer type), unique countries, unique continents

### 5.4 Data Processor Module

**File**: `data_processor.py` (~226 lines)

#### GDPDataProcessor (class)

| Method                     | Parameters        | Returns        | Description                                |
| -------------------------- | ----------------- | -------------- | ------------------------------------------ |
| `get_country_data`         | country, years    | numpy array    | GDP values for one country across years    |
| `get_continent_data`       | continent         | DataFrame      | All rows for a continent                   |
| `calculate_growth_rates`   | gdp_values, years | (rates, years) | Year-over-year % changes                   |
| `get_top_countries`        | year, n           | DataFrame      | Top N countries by GDP                     |
| `calculate_total_gdp`      | data, years       | Series         | Sum of GDP columns                         |
| `calculate_average_gdp`    | data, years       | Series         | Mean across year columns per row           |
| `get_correlation_matrix`   | countries, years  | DataFrame      | Pearson correlation matrix                 |
| `calculate_statistics`     | gdp_values        | dict           | max, min, mean, median, std, count         |
| `calculate_growth_summary` | gdp_values, years | dict           | total_growth, first/last value, avg annual |
| `get_continent_summary`    | continent, year   | dict           | total_gdp, avg_gdp, count, top 5           |
| `get_world_statistics`     | year              | dict           | total, avg, median, std, max, min, count   |
| `get_year_comparison_data` | years, continents | dict           | GDP by continent per year                  |
| `get_top_correlations`     | corr_matrix, n    | list           | Top N (country_a, country_b, correlation)  |

#### Module-Level Functions

| Function                                        | Description                      |
| ----------------------------------------------- | -------------------------------- |
| `filter_by_region(df, region)`                  | Filter DataFrame by continent    |
| `filter_by_country(df, country)`                | Filter DataFrame by country name |
| `calculate_regional_average(df, region, years)` | Average GDP for a continent      |
| `calculate_regional_sum(df, region, years)`     | Total GDP for a continent        |
| `calculate_country_average(df, country, years)` | Average GDP for a country        |
| `calculate_country_sum(df, country, years)`     | Total GDP for a country          |

All methods use FP constructs: `map()`, `filter()`, `reduce()`, `zip()`, `combinations()`. Zero loops.

### 5.5 Dashboard Controls & Interaction

#### Event Flow

```
User changes a control (country, continent, year, top N, analysis type)
    │
    ▼
on_analysis_change() / on_primary_country_change() / on_selection_change()
    │
    ▼
perform_analysis_delayed()  ──  300ms debounce via root.after()
    │
    ▼
perform_analysis()  ──  looks up analysis_map dict → calls the right method
    │
    ├──▶ Phase 1 method (e.g., plot_country_trend)
    │       ├── compute data via GDPDataProcessor
    │       ├── create matplotlib Figure
    │       ├── style with _style_figure() + _style_ax()
    │       ├── display_plot(fig) → FigureCanvasTkAgg in viz_frame
    │       └── show statistics in stats_text
    │
    └──▶ Phase 2 method (e.g., _run_engine_analysis)
            ├── _build_engine_params() reads UI controls
            ├── engine.run_analysis(name, params)
            └── tkinter_sink.write(results, title) → chart + table in GUI
```

#### Action Buttons

| Button                   | Action                                               |
| ------------------------ | ---------------------------------------------------- |
| 🔍 Analyze               | Manually triggers `perform_analysis()`               |
| 💾 Export Results to TXT | Saves statistics text to file (configurable path)    |
| 🗑️ Clear Visualization   | Destroys all widgets in viz_frame, clears stats_text |

#### Display Functions

- `display_plot(fig)`: Clears viz_frame, embeds matplotlib Figure via `FigureCanvasTkAgg`, sets dark background
- `_style_figure(fig)`: Applies dark face color from config
- `_style_ax(ax)`: Applies dark theme — hides top/right spines, sets colors, grid
- `_format_gdp(value)`: Formats GDP values as `$T`/`$B`/`$M`/`$0`
- `_force_white_text(widget)`: Recursively forces all labels to `#e7e9ea` and all buttons to white bg (overcomes ttkbootstrap theme conflicts)

---

## 6. Phase 2 — Modular Orchestration & Dependency Inversion

### 6.1 Objective

> Transition from a script-based approach to a Modular Architecture. Decouple the system so the Core (business logic) remains agnostic of data persistence and ingestion details.

The system is refactored into four packages: **Main** (Orchestrator), **Core** (Domain + Contracts), **Input Plugins** (Source), **Output Plugins** (Sink).

### 6.2 The Golden Rules — DIP Compliance

#### Rule 1: Inbound Abstraction ✅

> _"The Input Module must not depend on a concrete Core class."_

Evidence — `plugins/inputs.py`:

```python
from core.contracts import PipelineService   # Protocol, NOT concrete class

class CsvReader:
    def read_and_push(self, service: PipelineService) -> None:
        service.execute(records)              # Protocol method
```

All three readers (`CsvReader`, `JsonReader`, `ExcelReader`) accept `PipelineService` and call `service.execute()`. They never import `TransformationEngine`.

#### Rule 2: Outbound Abstraction ✅

> _"The Core must not import specific writers."_

Evidence — `core/engine.py`:

```python
from core.contracts import DataSink          # Its OWN protocol

class TransformationEngine:
    def __init__(self, sink: DataSink, config=None):
        self.sink: DataSink = sink            # Injected at runtime
```

`core/engine.py` has **zero imports from `plugins/`**. It calls `self.sink.write()` on the injected protocol.

#### Rule 3: Ownership of Contracts ✅

> _"The Core is the authority. It defines the contracts."_

All 3 Protocols are defined in `core/contracts.py`:

- `DataSink` — owned by Core, satisfied by output plugins
- `PipelineService` — owned by Core, satisfied by `TransformationEngine`
- `DataRecord` — owned by Core, structural type for GDP rows

#### Rule 4: Workflow ✅

> _"Main loads config → initializes Sink → initializes Engine (injects Sink) → initializes Input (passes Engine) → data flows via duck typing."_

`main.py`'s `run_pipeline()`:

```python
cfg = _load_config(config_path)                    # 1. Load config
sink = _create_output(output_drivers, ...)          # 2. Create Sink
engine = TransformationEngine(sink, cfg)            # 3. Create Engine, inject Sink
reader = _create_input(input_drivers, ...)          # 4. Create Reader
reader.read_and_push(engine)                        # 5. Data flows: Reader → Engine → Sink
```

### 6.3 Core Module — The Domain

#### `core/contracts.py` — Protocol Definitions

Three contracts using `typing.Protocol` + `@runtime_checkable`:

**DataRecord** — Structural type for a GDP row:

```python
@runtime_checkable
class DataRecord(Protocol):
    @property
    def country_name(self) -> str: ...
    @property
    def continent(self) -> str: ...
    @property
    def gdp_values(self) -> Dict[int, float]: ...
```

**DataSink** — Outbound abstraction (Core calls this to output):

```python
@runtime_checkable
class DataSink(Protocol):
    def write(self, records: List[Dict[str, Any]], title: str = "") -> None: ...
    def write_chart(self, chart_type: str, data: Dict[str, Any],
                    title: str = "", options: Optional[Dict[str, Any]] = None) -> None: ...
    def write_summary(self, summary: Dict[str, Any], title: str = "") -> None: ...
```

**PipelineService** — Inbound abstraction (Input modules call this):

```python
@runtime_checkable
class PipelineService(Protocol):
    def execute(self, raw_data: List[Dict[str, Any]]) -> None: ...
    def get_available_analyses(self) -> List[str]: ...
    def run_analysis(self, analysis_name: str,
                     params: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]: ...
```

#### `core/engine.py` — TransformationEngine

The engine implements `PipelineService` (structurally) and depends on `DataSink` (injected):

**Constructor — Dependency Injection:**

```python
class TransformationEngine:
    def __init__(self, sink: DataSink, config=None):
        self.sink: DataSink = sink
        self.config = config or {}
        self._dispatch = {
            'top_countries':             self._top_countries,
            'bottom_countries':          self._bottom_countries,
            'growth_rate':               self._growth_rate,
            'avg_gdp_by_continent':      self._avg_gdp_by_continent,
            'global_gdp_trend':          self._global_gdp_trend,
            'fastest_growing_continent': self._fastest_growing_continent,
            'consistent_decline':        self._consistent_decline,
            'continent_contribution':    self._continent_contribution,
        }
```

**Key Methods:**

| Method                        | Purpose                                                                                 |
| ----------------------------- | --------------------------------------------------------------------------------------- |
| `load_data(raw_data)`         | Converts `List[Dict]` → DataFrame, extracts year columns. Does NOT run analyses.        |
| `execute(raw_data)`           | Calls `load_data()` then runs all configured analyses, emitting each to `sink.write()`. |
| `run_analysis(name, params)`  | Runs a single analysis via `_dispatch` dict lookup. Returns `List[Dict]` or `None`.     |
| `get_available_analyses()`    | Returns tuple of 8 analysis names.                                                      |
| `_run_and_emit(name, params)` | Runs analysis + calls `self.sink.write(results, title)`.                                |

**Module-level helpers** (pure functions):

| Function                         | Purpose                           |
| -------------------------------- | --------------------------------- |
| `_safe_div(num, den)`            | Division with zero protection     |
| `_year_keys(row)`                | Extracts sorted integer keys      |
| `_raw_to_df(raw_data)`           | `List[Dict]` → `pd.DataFrame`     |
| `_resolve_years(df, date_range)` | Filters year columns within range |
| `_continent_df(df, continent)`   | DataFrame rows for one continent  |
| `_all_continents(df)`            | Sorted unique continent names     |

#### `core/__init__.py`

```python
from core.contracts import DataSink, PipelineService, DataRecord
__all__ = ['DataSink', 'PipelineService', 'DataRecord']
```

### 6.4 Input Module — The Source

**File**: `plugins/inputs.py` (~78 lines)

Three readers, all interchangeable via `config.json`:

| Class         | Format  | Library             | Key Logic                                               |
| ------------- | ------- | ------------------- | ------------------------------------------------------- |
| `CsvReader`   | `.csv`  | `pandas.read_csv`   | `_df_to_records(df)` → `service.execute(records)`       |
| `JsonReader`  | `.json` | `json.load`         | `_coerce_year_keys(record)` to fix string→int year keys |
| `ExcelReader` | `.xlsx` | `pandas.read_excel` | `_df_to_records(df)` → `service.execute(records)`       |

**Shared interface**: `read_and_push(self, service: PipelineService)`

All three:

- Accept `PipelineService` (Protocol) — never a concrete class
- Call `service.execute(records)` — the Protocol method
- Are "blind" to Core internals
- Convert data to `List[Dict[str, Any]]` with integer year keys

**Helper functions:**

- `_df_to_records(df)` — Converts DataFrame to list of dicts, renaming string year columns to integers
- `_coerce_year_keys(record)` — Converts string keys like `"2020"` to integer `2020` in a single dict

**Swapping input**: Change one field in `config.json`:

```json
"pipeline": { "input_driver": "csv" }   // or "json" or "excel"
```

### 6.5 Output Module — The Sink

**File**: `plugins/outputs.py` (~470 lines)

Three writers, all satisfying `DataSink` Protocol:

#### ConsoleWriter

Outputs formatted ASCII tables to stdout.

```
======================================================================
  TOP COUNTRIES
======================================================================

  rank    country              continent    year     gdp
  -------------------------------------------------------------------
  1       China                Asia         2020     $15.00T
  2       Japan                Asia         2020     $5.05T
```

- `write()` — prints header + formatted column rows
- `write_chart()` — text representation of chart data
- `write_summary()` — key-value text block
- GDP auto-formatted: `$T`, `$B`, `$M`

#### GraphicsChartWriter

Saves matplotlib charts as PNG files.

- Supports: `bar`, `line`, `pie`, `grouped_bar`, `heatmap`
- Creates `output_charts/` directory, saves numbered PNG files
- Uses dark theme from `config.json` visualization settings
- `write()` auto-detects best chart type from record keys

#### TkinterSink

Renders charts and tables directly inside the GUI dashboard.

- `bind(viz_frame, stats_text, notebook)` — connects to dashboard widgets after creation
- `write()` — renders chart via `FigureCanvasTkAgg` in viz_frame + formatted table in stats_text
- `write_chart()` — chart rendering only (bar, line, pie)
- `write_summary()` — text summary in stats_text
- Before `bind()` is called, all methods silently no-op (prevents init-time errors)
- Auto-selects the Visualization tab after rendering

**Swapping output**: Change one field in `config.json`:

```json
"pipeline": { "output_driver": "chart" }  // or "console" or "tkinter"
```

### 6.6 Main Module — The Orchestrator

**File**: `main.py` (~140 lines)

The entry point that:

1. Reads `config.json` to determine runtime behavior
2. Uses a **Dictionary-based Factory** with `importlib` to instantiate components
3. Performs **Dependency Injection** by wiring components together
4. Starts execution

#### Factory System

```python
_load_config = lambda path: json.loads(open(path, 'r', encoding='utf-8').read())

def _resolve_class(driver_entry):
    module = importlib.import_module(driver_entry['module'])  # e.g., "plugins.inputs"
    return getattr(module, driver_entry['class'])              # e.g., "ExcelReader"

def _build_driver_map(cfg, section):
    return dict(map(
        lambda kv: (kv[0], _resolve_class(kv[1])),
        cfg.get(section, {}).items(),
    ))
```

`_resolve_class` uses `importlib.import_module` for dynamic class loading. To add a new plugin:

1. Create a class satisfying the relevant Protocol
2. Add its `module:class` entry to `config.json`
3. Zero changes to Core or main.py

#### Wiring (run_pipeline)

```python
def run_pipeline():
    cfg = _load_config('config.json')
    input_drivers = _build_driver_map(cfg, 'input_drivers')    # {"excel": ExcelReader, ...}
    output_drivers = _build_driver_map(cfg, 'output_drivers')  # {"console": ConsoleWriter, ...}

    sink = _create_output(output_drivers, "console", cfg)      # Step 1: Create Sink
    reader = _create_input(input_drivers, "excel", path)       # Step 2: Create Reader
    engine = TransformationEngine(sink, cfg)                   # Step 3: Inject Sink into Engine
    reader.read_and_push(engine)                               # Step 4: Reader → Engine → Sink
```

#### GUI Launch

```python
def run_gui():
    from gdp_dashboard_refactored import main as launch_dashboard
    launch_dashboard()
```

#### CLI Modes

| Command                 | Mode                              |
| ----------------------- | --------------------------------- |
| `python main.py`        | GUI dashboard (default)           |
| `python main.py --gui`  | GUI dashboard (explicit)          |
| `python main.py --cli`  | Console pipeline (all 8 analyses) |
| `python main.py <name>` | Single analysis (console)         |
| `python main.py --list` | List analysis names               |
| `python main.py --help` | Usage info                        |

### 6.7 All 8 Phase 2 Analyses

#### 1. Top 10 Countries by GDP (`top_countries`)

**Parameters**: `continent` (default: Asia), `year` (default: latest), `top_n` (default: 10)  
**Output**: Ranked list of top N countries in a continent for a specific year.

| Field       | Type  | Description  |
| ----------- | ----- | ------------ |
| `rank`      | int   | Position 1–N |
| `country`   | str   | Country name |
| `continent` | str   | Continent    |
| `year`      | int   | Year         |
| `gdp`       | float | GDP value    |

#### 2. Bottom 10 Countries by GDP (`bottom_countries`)

Same parameters and schema as top countries but returns the smallest GDP values. NaN rows filtered before ranking.

#### 3. GDP Growth Rate by Country (`growth_rate`)

**Parameters**: `continent`, `date_range` [start, end]  
**Output**: Every country ranked by growth percentage.

| Field                     | Type  | Description       |
| ------------------------- | ----- | ----------------- |
| `country`                 | str   | Country name      |
| `continent`               | str   | Continent         |
| `start_year` / `end_year` | int   | Range boundaries  |
| `start_gdp` / `end_gdp`   | float | GDP at start/end  |
| `growth_pct`              | float | Growth percentage |

Sorted descending. Countries with zero start GDP or NaN excluded.

#### 4. Average GDP by Continent (`avg_gdp_by_continent`)

**Parameters**: `date_range`  
**Output**: Average GDP per continent across date range.

| Field                     | Type  | Description            |
| ------------------------- | ----- | ---------------------- |
| `continent`               | str   | Continent name         |
| `avg_gdp`                 | float | Average GDP            |
| `start_year` / `end_year` | int   | Range                  |
| `country_count`           | int   | Countries in continent |

#### 5. Total Global GDP Trend (`global_gdp_trend`)

**Parameters**: `date_range`  
**Output**: Year-by-year total world GDP.

| Field           | Type  | Description         |
| --------------- | ----- | ------------------- |
| `year`          | int   | Year                |
| `total_gdp`     | float | Global sum          |
| `country_count` | int   | Countries with data |

#### 6. Fastest Growing Continent (`fastest_growing_continent`)

**Parameters**: `date_range`  
**Output**: Continents ranked by total GDP growth.

| Field                     | Type  | Description            |
| ------------------------- | ----- | ---------------------- |
| `continent`               | str   | Continent              |
| `start_year` / `end_year` | int   | Range                  |
| `start_gdp` / `end_gdp`   | float | Total GDP at start/end |
| `growth_pct`              | float | Percentage growth      |

#### 7. Countries with Consistent GDP Decline (`consistent_decline`)

**Parameters**: `decline_years` (default: 5)  
**Output**: Countries where GDP declined every consecutive year for X years.

| Field                     | Type  | Description       |
| ------------------------- | ----- | ----------------- |
| `country`                 | str   | Country name      |
| `continent`               | str   | Continent         |
| `decline_years`           | int   | Consecutive years |
| `start_year` / `end_year` | int   | Decline period    |
| `start_gdp` / `end_gdp`   | float | GDP at start/end  |
| `decline_pct`             | float | Total decline %   |

Uses `all(map(lambda p: p[1] < p[0], pairs))` — no loops.

#### 8. Continent Contribution to Global GDP (`continent_contribution`)

**Parameters**: `date_range`  
**Output**: Each continent's share of total global GDP.

| Field                     | Type  | Description       |
| ------------------------- | ----- | ----------------- |
| `continent`               | str   | Continent         |
| `total_gdp`               | float | Continent's total |
| `global_total_gdp`        | float | World total       |
| `contribution_pct`        | float | Percentage share  |
| `start_year` / `end_year` | int   | Range             |

### 6.8 GUI Integration of Phase 2

The Phase 2 engine is fully wired into the Phase 1 dashboard:

1. **Initialization** (`gdp_dashboard_refactored.py`):

   ```python
   self.tkinter_sink = TkinterSink(raw_config)
   self.engine = TransformationEngine(self.tkinter_sink, raw_config)
   self.engine.load_data(_df_to_records(self.df))   # Load only, don't run
   ```

2. **Widget binding** (after `create_widgets()`):

   ```python
   self.tkinter_sink.bind(self.viz_frame, self.stats_text, self.notebook)
   ```

3. **9 Radio buttons** in sidebar (from `config.json`'s `analysis_types`):
   - ⚡ Top Countries (Engine), ⚡ Bottom Countries (Engine), ⚡ Growth Rate (Engine)
   - ⚡ Avg GDP by Continent, ⚡ Global GDP Trend, ⚡ Fastest Growing Continent
   - ⚡ Consistent Decline, ⚡ Continent Contribution
   - ⚡ Run All Engine Analyses

4. **Parameter bridging** — `_build_engine_params()` reads dashboard controls:

   ```python
   {'continent': ..., 'year': ..., 'date_range': [...], 'top_n': ..., 'decline_years': 5}
   ```

5. **Execution** — `_run_engine_analysis(name)`:
   - Clears stats text
   - Calls `engine.run_analysis(name, params)`
   - Passes results to `tkinter_sink.write(results, title)`

6. **Run All** — `_run_all_engine_analyses()`:
   - Runs all 8, appends each table to stats text
   - Shows composite chart, switches to Statistics tab

---

## 7. Configuration System — config.json

The entire application is driven by `config.json` (~243 lines). Every section is documented below:

### `pipeline` — Phase 2 Pipeline Settings

```json
{
    "input_driver": "excel",
    "output_driver": "console",
    "data_source": "gdp_with_continent_filled.xlsx",
    "analyses": ["top_countries", "bottom_countries", ...],
    "default_params": {
        "continent": "Asia", "year": 2020,
        "date_range": [2000, 2020], "top_n": 10, "decline_years": 5
    }
}
```

### `input_drivers` / `output_drivers` — Plugin Registry

```json
{
  "input_drivers": {
    "csv": { "class": "CsvReader", "module": "plugins.inputs" },
    "json": { "class": "JsonReader", "module": "plugins.inputs" },
    "excel": { "class": "ExcelReader", "module": "plugins.inputs" }
  },
  "output_drivers": {
    "console": { "class": "ConsoleWriter", "module": "plugins.outputs" },
    "chart": { "class": "GraphicsChartWriter", "module": "plugins.outputs" },
    "tkinter": { "class": "TkinterSink", "module": "plugins.outputs" }
  }
}
```

To add a new plugin: add its `class` + `module` entry here. Zero code changes elsewhere.

### `data` — Data File Settings

```json
{
  "file_path": "gdp_with_continent_filled.xlsx",
  "required_columns": ["Country Name", "Continent"],
  "export_file": "gdp_analysis_report.txt"
}
```

### `ui` — Dashboard Window Settings

```json
{
  "window_width": 1400,
  "window_height": 900,
  "title": "GDP Analysis Dashboard",
  "title_emoji": "🌍 GDP Analysis Dashboard 📊",
  "title_bar_height": 80,
  "left_panel_width": 350,
  "default_top_n": 10,
  "max_compare_countries": 10,
  "max_correlation_countries": 15,
  "update_delay_ms": 300
}
```

### `colors` — X/Twitter Dark Theme Palette

20+ color keys: `primary` (#1d9bf0), `dark` (#0a0a0a), `text_primary` (#e7e9ea), `text_secondary` (#71767b), `dark_border` (#2f3336), `chart_palette` (10 colors), plus neon variants.

### `analysis_types` — Sidebar Radio Buttons

Array of 20+ entries, each with `name` (display text) and `value` (dispatch key). Includes disabled separator entries for section headers.

### `visualization` — Chart Rendering Settings

```json
{
  "figure_size": [12, 6],
  "style": "dark_background",
  "chart_bg_color": "#000000",
  "chart_face_color": "#000000",
  "grid_color": "#2f3336",
  "grid_alpha": 0.3,
  "title_font_size": 16,
  "label_font_size": 12,
  "tick_font_size": 9,
  "use_cyberpunk": true
}
```

### `phase1_filters` — Default Selections

```json
{ "region": "Asia", "year": "2020", "country": "Pakistan" }
```

### `phase1_operations` — Computation Defaults

```json
{
  "statistical_operation": "average",
  "compute_regions": [
    "Asia",
    "Europe",
    "Africa",
    "North America",
    "South America",
    "Oceania"
  ],
  "compute_countries": [
    "Pakistan",
    "India",
    "China",
    "United States",
    "Germany"
  ]
}
```

### `phase1_visualizations` — Chart Type Selection

```json
{
  "region_charts": ["pie", "bar"],
  "year_charts": ["line", "scatter"],
  "enable_histogram": true
}
```

---

## 8. Data Flow — End-to-End Workflows

### CLI Pipeline (`python main.py --cli`)

```
config.json
    │
    ▼
main.py: _load_config() ──────────────────────────────────────────────────────
    │                                                                          │
    ├──▶ _build_driver_map('input_drivers')  ──▶ {"excel": ExcelReader}       │
    ├──▶ _build_driver_map('output_drivers') ──▶ {"console": ConsoleWriter}   │
    │                                                                          │
    ├──▶ ConsoleWriter(config=cfg)           ── Step 1: Create Sink           │
    ├──▶ ExcelReader(file_path=path)         ── Step 2: Create Reader         │
    ├──▶ TransformationEngine(sink, cfg)     ── Step 3: Inject Sink           │
    │                                                                          │
    └──▶ reader.read_and_push(engine)        ── Step 4:                       │
              │                                                                │
              ├──▶ pd.read_excel(file_path)                                   │
              ├──▶ _df_to_records(df)                                         │
              └──▶ engine.execute(records)                                    │
                        │                                                      │
                        ├──▶ load_data(records) → DataFrame                   │
                        └──▶ for each analysis: _dispatch → sink.write()      │
                                                     │                         │
                                                     └──▶ ConsoleWriter prints │
```

### GUI Launch (`python main.py`)

```
main.py: run_gui()
    └──▶ gdp_dashboard_refactored.main()
              ├──▶ tk.Tk() + ttkbootstrap "darkly"
              └──▶ GDPDashboard(root)
                        ├── ConfigLoader → config.json
                        ├── GDPDataLoader → Excel → DataFrame
                        ├── GDPDataProcessor(df, years)          [Phase 1]
                        ├── TkinterSink(config)                  [Phase 2 Sink]
                        ├── TransformationEngine(sink, config)   [Phase 2 Engine]
                        ├── engine.load_data(records)            [Load only]
                        ├── create_widgets()
                        ├── tkinter_sink.bind(viz, stats, nb)    [Connect]
                        └── root.mainloop()
                              │
                              ├── User selects Phase 1 analysis
                              │   └── plot_*() → GDPDataProcessor → matplotlib
                              │
                              └── User selects Phase 2 analysis (⚡)
                                  └── _run_engine_analysis()
                                      → engine.run_analysis()
                                      → tkinter_sink.write() → GUI renders
```

**The same `TransformationEngine` and 8 analyses work in CLI and GUI.** Only the injected `DataSink` differs.

---

## 9. Functional Programming Compliance

**Requirement**: Zero `for`/`while` loops across the entire codebase.

**Verification:**

```bash
Select-String -Pattern '^\s+for \w+ in |^\s+while ' -Path *.py,core\*.py,plugins\*.py
# Result: zero matches
```

### FP Constructs Used Throughout

| Construct           | Purpose            | Example                                                        |
| ------------------- | ------------------ | -------------------------------------------------------------- |
| `map()`             | Transform elements | `list(map(lambda r: r['gdp'], records))`                       |
| `filter()`          | Select elements    | `filter(lambda c: isinstance(c, int), df.columns)`             |
| `reduce()`          | Accumulate         | `reduce(lambda acc, y: acc + df[y].sum(), years, 0.0)`         |
| `sorted()`          | Order              | `sorted(results, key=lambda r: r['growth_pct'], reverse=True)` |
| `zip()`             | Pair elements      | `zip(vals[:-1], vals[1:])`                                     |
| `all()`             | Universal check    | `all(map(lambda p: p[1] < p[0], pairs))`                       |
| `any()`             | Existential check  | `any(map(pd.isna, vals))`                                      |
| `lambda`            | Inline functions   | Used throughout                                                |
| `enumerate()`       | Indexed iteration  | `enumerate(top.iterrows(), 1)`                                 |
| `next(filter(...))` | First match        | `next(filter(lambda k: k in ('country',), keys), keys[0])`     |
| `dict(map(...))`    | Dict construction  | Driver maps from config                                        |
| `combinations()`    | Pair generation    | Correlation pairs in `data_processor.py`                       |

### Where FP is applied:

- **`core/engine.py`**: All 8 analyses use `map`, `filter`, `reduce`, `sorted` — zero loops
- **`plugins/inputs.py`**: Record conversion via `map` + `lambda`
- **`plugins/outputs.py`**: Table formatting via `map`, child destruction via `map`
- **`main.py`**: Driver map construction via `dict(map(...))`
- **`data_loader.py`**: Validation via `filter` (missing sections, missing columns)
- **`data_processor.py`**: Growth rates, correlations, statistics — all via FP
- **`gdp_dashboard_refactored.py`**: Listbox population, widget recursion, radio button creation
- **`test_dashboard.py`**: Test counting via `reduce`

---

## 10. Data-Driven Programming

All runtime behavior is controlled by `config.json`:

| What changes      | Config field                          | Effect                                        |
| ----------------- | ------------------------------------- | --------------------------------------------- |
| Input format      | `pipeline.input_driver`               | Switches between CSV/JSON/Excel reader        |
| Output format     | `pipeline.output_driver`              | Switches between Console/Chart/Tkinter writer |
| Data file         | `pipeline.data_source`                | Points to different data files                |
| Which analyses    | `pipeline.analyses`                   | Controls which of 8 analyses run              |
| Parameters        | `pipeline.default_params`             | Default continent, year, date_range, top_n    |
| Window size       | `ui.window_width/height`              | Dashboard dimensions                          |
| Theme colors      | `colors.*`                            | Entire visual theme                           |
| Chart sizes       | `visualization.figure_size`           | Plot dimensions                               |
| Chart styles      | `visualization.style`                 | Matplotlib style                              |
| Default country   | `phase1_filters.country`              | Pre-selected country                          |
| Default region    | `phase1_filters.region`               | Pre-selected continent                        |
| Compare countries | `phase1_operations.compute_countries` | Pre-selected in listbox                       |
| Analysis labels   | `analysis_types[].name`               | Radio button display text                     |
| Chart types       | `phase1_visualizations.region_charts` | Which charts to render                        |

**No hardcoded values** — all defaults come from config. Adding a new plugin requires zero code changes to Core or Main.

---

## 11. PlantUML Architecture Diagram

**File**: `architecture.puml` (~193 lines)

The diagram visualizes the complete DIP architecture:

- **Core package**: `DataSink`, `PipelineService`, `DataRecord` protocols + `TransformationEngine`
- **Input plugins**: `CsvReader`, `JsonReader`, `ExcelReader` → arrows to `PipelineService`
- **Output plugins**: `ConsoleWriter`, `GraphicsChartWriter`, `TkinterSink` → satisfy `DataSink`
- **Orchestrator**: `main.py` creates and wires all components
- **Dashboard**: `GDPDashboard` uses engine + TkinterSink
- **Config + Data**: External dependencies shown as databases
- **Notes**: Golden Rules summary + CLI usage

**Theme**: Dark styling matching X/Twitter palette (`#0a0a0a` background, `#1d9bf0` arrows, `#2f3336` borders).

**To render**: Use [plantuml.com](http://www.plantuml.com/plantuml/uml/) or any PlantUML tool. Paste contents of `architecture.puml`.

---

## 12. Testing

### Test Suite — `test_dashboard.py` (8 Tests)

| #   | Test                     | What it verifies                                                 |
| --- | ------------------------ | ---------------------------------------------------------------- |
| 1   | Data Loading             | Excel loads, has `Country Name` + `Continent` columns            |
| 2   | Data Structure           | Year columns exist in range 1960–2030                            |
| 3   | Data Integrity           | Required columns present, no null names, continents exist        |
| 4   | Numerical Data           | GDP data points exist, warns on negatives                        |
| 5   | Required Libraries       | `pandas`, `numpy`, `matplotlib`, `seaborn`, `tkinter` importable |
| 6   | Basic Analysis           | `nlargest`, continent filtering, year subsetting work            |
| 7   | Statistical Calculations | Mean, median, std, growth rate compute correctly                 |
| 8   | Data Coverage            | Reports % of non-null GDP cells (~84.2%)                         |

**Running:**

```bash
python test_dashboard.py
```

**Expected output:**

```
============================================================
  GDP DASHBOARD TEST SUITE
============================================================

Test 1: Data Loading... ✓ PASSED
Test 2: Data Structure... ✓ PASSED
Test 3: Data Integrity... ✓ PASSED
Test 4: Numerical Data... ✓ PASSED
Test 5: Required Libraries... ✓ PASSED
Test 6: Basic Analysis... ✓ PASSED
Test 7: Statistical Calculations... ✓ PASSED
Test 8: Data Coverage... ✓ PASSED (Coverage: 84.2%)

============================================================
  TEST RESULTS: 8/8 PASSED
============================================================
```

### Manual Verification

```bash
python main.py --cli           # All 8 Phase 2 analyses in console
python main.py top_countries   # Single analysis
python main.py --list          # List analyses
python main.py                 # GUI — test all 20 analysis radio buttons
```

---

## 13. Dependencies

**File**: `requirements.txt`

| Package        | Version | Purpose                            |
| -------------- | ------- | ---------------------------------- |
| `pandas`       | ≥2.0.0  | DataFrame operations, data loading |
| `openpyxl`     | ≥3.0.0  | Excel file reading                 |
| `matplotlib`   | ≥3.5.0  | Chart rendering (all phases)       |
| `seaborn`      | ≥0.12.0 | Correlation heatmaps               |
| `numpy`        | ≥1.21.0 | Numerical operations               |
| `mplcyberpunk` | ≥0.7.0  | Glow effects on line charts        |
| `ttkbootstrap` | ≥1.10.0 | Dark themed tkinter widgets        |

### Standard Library

`tkinter`, `json`, `os`, `sys`, `importlib`, `functools`, `itertools`, `warnings`, `typing`

---

## 14. Deliverables Checklist

### Phase 1 Deliverables

| #   | Deliverable                       | Status                                         |
| --- | --------------------------------- | ---------------------------------------------- |
| 1   | Interactive GUI dashboard         | ✅ tkinter + ttkbootstrap                      |
| 2   | 11 analysis types                 | ✅ All implemented                             |
| 3   | Config-driven behavior            | ✅ `config.json` controls everything           |
| 4   | Functional programming (no loops) | ✅ Zero for/while loops                        |
| 5   | Data-driven programming           | ✅ All parameters from config                  |
| 6   | Statistical calculations          | ✅ `GDPDataProcessor`                          |
| 7   | Multiple chart types              | ✅ Line, bar, pie, scatter, heatmap, histogram |
| 8   | Export functionality              | ✅ Export to TXT                               |
| 9   | Professional dark theme           | ✅ X/Twitter dark aesthetic                    |

### Phase 2 Deliverables

| #   | Deliverable                          | Status                                                |
| --- | ------------------------------------ | ----------------------------------------------------- |
| 1   | Modular package structure            | ✅ `core/`, `plugins/`, `data/` with `__init__.py`    |
| 2   | `config.json` for IO swapping        | ✅ `input_drivers`, `output_drivers` sections         |
| 3   | Architecture diagram (PlantUML)      | ✅ `architecture.puml` (193 lines)                    |
| 4   | PlantUML code                        | ✅ Full dark-themed diagram                           |
| 5   | Graphical representation             | ✅ Renderable via any PlantUML tool                   |
| 6   | Structural Python code from PlantUML | ✅ All classes match diagram exactly                  |
| 7   | Full implementation                  | ✅ 8 analyses, 3 inputs, 3 outputs                    |
| 8   | Protocol contracts (DIP)             | ✅ `DataSink`, `PipelineService`, `DataRecord`        |
| 9   | Inbound Abstraction                  | ✅ Inputs use `PipelineService` Protocol              |
| 10  | Outbound Abstraction                 | ✅ Engine uses `DataSink` Protocol, injected          |
| 11  | Ownership of Contracts               | ✅ Core defines all protocols                         |
| 12  | Orchestrator (Main Module)           | ✅ `main.py` — importlib factory, DI wiring           |
| 13  | ≥2 Input implementations             | ✅ 3: CsvReader, JsonReader, ExcelReader              |
| 14  | ≥2 Output implementations            | ✅ 3: ConsoleWriter, GraphicsChartWriter, TkinterSink |
| 15  | 8 required analyses                  | ✅ All in `core/engine.py` via dispatch dict          |
| 16  | FP compliance maintained             | ✅ Zero loops in all new code                         |
| 17  | Data-driven programming              | ✅ All behavior from config                           |
| 18  | GUI integration                      | ✅ Phase 2 analyses in dashboard                      |

---

## 15. Standard Library Tools Used

| Tool                       | Requirement       | Usage                                                              |
| -------------------------- | ----------------- | ------------------------------------------------------------------ |
| `typing.Protocol`          | Required          | Structural interfaces: `DataSink`, `PipelineService`, `DataRecord` |
| `typing.runtime_checkable` | Required          | Enables `isinstance()` checks on Protocols                         |
| `json`                     | Required          | Parse `config.json` throughout                                     |
| `importlib`                | Optional/Advanced | Dynamic class loading in `main.py` factory                         |
| `functools.reduce`         | Phase 1 req       | Accumulation throughout (GDP sums, test counting)                  |
| `sys`                      | —                 | CLI argument handling                                              |
| `os`                       | —                 | File existence checks                                              |
| `itertools.combinations`   | —                 | Correlation pair generation                                        |
| `warnings`                 | —                 | Suppress matplotlib warnings                                       |

**Note**: `abc.ABC` was not used — `typing.Protocol` provides structural typing without requiring inheritance, which is more Pythonic and aligned with duck typing.

---

## 16. Troubleshooting

| Issue                                 | Cause                   | Solution                                                   |
| ------------------------------------- | ----------------------- | ---------------------------------------------------------- |
| `FileNotFoundError: config.json`      | Wrong working directory | Run from `proj/` directory                                 |
| `ModuleNotFoundError: core.contracts` | Wrong working directory | Ensure `core/` exists relative to cwd                      |
| `UnicodeDecodeError` on config        | Encoding mismatch       | File loaded with `encoding='utf-8'` — save config as UTF-8 |
| `Unknown input driver`                | Typo in config          | Check `config.json` → `input_drivers` keys                 |
| `Unknown output driver`               | Typo in config          | Check `config.json` → `output_drivers` keys                |
| Dashboard won't launch                | Missing dependencies    | `pip install -r requirements.txt`                          |
| Charts not showing in GUI             | TkinterSink not bound   | Sink binds after `create_widgets()` — automatic            |
| `No data available` for analysis      | Wrong continent name    | Continent names are case-sensitive (match data)            |
| Excel file not found                  | Missing data file       | Place `gdp_with_continent_filled.xlsx` in `proj/`          |
| Visualization not updating            | Stale state             | Click "Clear Visualization" then re-analyze                |
| Slow with many countries              | Too many comparisons    | Reduce to ≤10 countries in compare listbox                 |
| `Failed to load data`                 | Corrupted Excel         | Re-download the data file                                  |
| Blank chart after Phase 2 analysis    | No matching data        | Verify continent has data for selected year range          |

---

## Data

- **Source file**: `gdp_with_continent_filled.xlsx`
- **Rows**: 266 countries and regions
- **Columns**: Country Name, Country Code, Indicator Name, Indicator Code, 1960–2024 (65 year columns), Continent
- **Coverage**: ~84.2% (non-null GDP values)
- **Continents**: Africa, Asia, Europe, Global, North America, Oceania, South America

---

**End of Documentation**
