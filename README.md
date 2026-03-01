# GDP Analysis Dashboard

A comprehensive interactive dashboard for analyzing and visualizing GDP data across 266 countries and continents from 1960 to 2024. Built with two execution phases: a rich tkinter GUI (Phase 1) and a modular DIP engine with runtime-selectable analyses (Phase 2).

---

## Quick Start

```bash
pip install -r requirements.txt
python gdp_dashboard_refactored.py
```

Or double-click `launch_dashboard.bat` on Windows.

### Via main.py (single entry point)

```bash
python main.py                        # Launch GUI dashboard (default)
python main.py --gui                  # Launch GUI dashboard (explicit)
python main.py --cli                  # Run all 8 analyses in console
python main.py top_countries           # Run a single analysis (console)
python main.py --list                  # List available analyses
```

Change `pipeline.output_driver` in `config.json` to `"chart"` to save PNG files instead of printing to console.

### Prerequisites

- Python 3.10+
- The data file `gdp_with_continent_filled.xlsx` in the project root

### Verify Installation

```bash
python test_dashboard.py
```

---

## Project Structure

```
proj/
├── gdp_dashboard_refactored.py   # Main GUI dashboard application
├── main.py                        # CLI orchestrator (full pipeline / single analysis)
├── architecture.puml              # PlantUML architecture diagram
├── data_loader.py                 # ConfigLoader, GDPDataLoader
├── data_processor.py              # GDPDataProcessor (statistics, filtering)
├── test_dashboard.py              # Automated test suite (8 tests)
├── config.json                    # All runtime configuration
├── requirements.txt               # Python dependencies
├── launch_dashboard.bat           # Windows launcher
├── gdp_with_continent_filled.xlsx # GDP dataset (266 countries, 1960-2024)
├── core/
│   ├── __init__.py                # Re-exports: DataSink, PipelineService, DataRecord
│   ├── contracts.py               # Protocol definitions (DIP contracts)
│   └── engine.py                  # TransformationEngine (8 analyses)
├── plugins/
│   ├── __init__.py
│   ├── inputs.py                  # CsvReader, JsonReader, ExcelReader
│   └── outputs.py                 # ConsoleWriter, GraphicsChartWriter, TkinterSink
└── data/
    └── __init__.py
```

---

## Features

### Phase 1 — Interactive Dashboard (11 Analysis Types)

| #   | Analysis             | Description                                     |
| --- | -------------------- | ----------------------------------------------- |
| 1   | Country GDP Trend    | Line chart of GDP over time for one country     |
| 2   | Compare Countries    | Multi-line comparison (up to 10 countries)      |
| 3   | Continent Analysis   | 4-panel: trend, top 10, avg GDP, histogram      |
| 4   | Top Countries        | Horizontal bar chart with rankings              |
| 5   | GDP Growth Rate      | Year-over-year % change (green/red bars)        |
| 6   | Statistical Summary  | Full text report with rankings by continent     |
| 7   | Year Comparison      | Grouped bars comparing continents across years  |
| 8   | Correlation Analysis | Heatmap of GDP correlations between countries   |
| 9   | Regional Analysis    | Pie + bar charts for continent GDP distribution |
| 10  | Year Analysis        | Line + scatter for a single country             |
| 11  | Complete Analysis    | All 4 chart types on one page                   |

### Phase 2 — Engine Analyses (9 Selectable at Runtime)

| #   | Analysis                  | Output                                 |
| --- | ------------------------- | -------------------------------------- |
| 1   | Top Countries (Engine)    | Bar chart + table of top N by GDP      |
| 2   | Bottom Countries (Engine) | Bar chart + table of bottom N          |
| 3   | Growth Rate (Engine)      | Country growth rankings in a continent |
| 4   | Avg GDP by Continent      | Average GDP per continent              |
| 5   | Global GDP Trend          | Total world GDP per year               |
| 6   | Fastest Growing Continent | Continent growth rankings              |
| 7   | Consistent Decline        | Countries with consecutive GDP decline |
| 8   | Continent Contribution    | Each continent's % of global GDP       |
| 9   | Run All Engine Analyses   | All 8 above, results in Statistics tab |

All Phase 2 analyses respect dashboard controls (continent, year range, top N) and render directly in the GUI.

---

## Using the Dashboard

1. **Select Analysis Type** — Radio buttons on the left panel (Phase 1 and Phase 2 separated by header)
2. **Set Parameters** — Country, continent, year range, top N
3. **Click "Analyze"** or just change a selection — the chart updates automatically
4. **View Results** — Visualization tab for charts, Statistics tab for tables
5. **Export** — Click "Export Results to TXT" to save the Statistics tab content

---

## Architecture

### Phase 1 (GUI Layer)

- `GDPDashboard` — tkinter + ttkbootstrap ("darkly" / X-Twitter dark theme)
- `data_loader.py` — `ConfigLoader` reads `config.json`, `GDPDataLoader` loads Excel
- `data_processor.py` — `GDPDataProcessor` for statistics, filtering, correlation

### Phase 2 (Modular Engine — Dependency Inversion Principle)

```
Input Plugin ──► PipelineService (Protocol) ──► TransformationEngine
                                                       │
                                              DataSink (Protocol)
                                                       │
                                              TkinterSink / ConsoleWriter / GraphicsChartWriter
```

**Core owns all contracts** — plugins depend on protocols, never the reverse.

#### `core/contracts.py` — Protocol Definitions

| Protocol          | Methods                                                   | Purpose                       |
| ----------------- | --------------------------------------------------------- | ----------------------------- |
| `DataRecord`      | `country_name`, `continent`, `gdp_values`                 | Structural type for a GDP row |
| `DataSink`        | `write()`, `write_chart()`, `write_summary()`             | Outbound — render results     |
| `PipelineService` | `execute()`, `get_available_analyses()`, `run_analysis()` | Inbound — receive raw data    |

All use `typing.Protocol` + `@runtime_checkable` for structural (duck) typing.

#### `core/engine.py` — TransformationEngine

- Implements `PipelineService`
- 8 analyses via dictionary-based dispatch (no if/elif chains)
- `DataSink` injected via constructor
- `execute()` loads data + runs configured analyses
- `run_analysis(name, params)` runs a single named analysis on demand

#### `plugins/inputs.py` — Input Plugins

| Class         | Format  | Library             |
| ------------- | ------- | ------------------- |
| `CsvReader`   | `.csv`  | `pandas.read_csv`   |
| `JsonReader`  | `.json` | `json.load`         |
| `ExcelReader` | `.xlsx` | `pandas.read_excel` |

Each calls `service.execute(records)` — zero knowledge of Core internals.

#### `plugins/outputs.py` — Output Plugins

| Class                 | Output        | Description                                              |
| --------------------- | ------------- | -------------------------------------------------------- |
| `ConsoleWriter`       | stdout        | Formatted ASCII tables                                   |
| `GraphicsChartWriter` | PNG files     | matplotlib charts (bar, line, pie, grouped_bar, heatmap) |
| `TkinterSink`         | Dashboard GUI | Renders charts + tables directly in the tkinter app      |

`TkinterSink.bind(viz_frame, stats_text, notebook)` connects to the dashboard widgets at startup.

---

## Configuration (`config.json`)

| Section                            | Purpose                                                      |
| ---------------------------------- | ------------------------------------------------------------ |
| `pipeline`                         | Input/output driver selection, analysis list, default params |
| `input_drivers` / `output_drivers` | Class → module maps for driver discovery                     |
| `data`                             | File path, required columns, export file                     |
| `ui`                               | Window size, panel widths, defaults                          |
| `colors`                           | Full X/Twitter dark theme palette                            |
| `analysis_types`                   | Radio button labels + values for the sidebar                 |
| `visualization`                    | Figure sizes, chart bg/face colors, fonts, grid              |
| `phase1_filters`                   | Default country, region, year                                |
| `phase1_operations`                | Regions, countries, statistical operation                    |
| `phase1_visualizations`            | Chart type lists per analysis                                |

---

## FP Compliance

All modules maintain zero `for`/`while` loops:

- Iteration: `map()`, `filter()`, `reduce()`, `sorted()`, `zip()`, `all()`, `any()`
- Inline transforms: lambdas
- Accumulation: `functools.reduce`

---

## Data

- **Source**: `gdp_with_continent_filled.xlsx`
- **Rows**: 266 countries/regions
- **Columns**: Country Name, Country Code, Indicator Name, Indicator Code, 1960–2024, Continent
- **Coverage**: ~84.2%

---

## Dependencies

```
pandas>=2.0.0
openpyxl>=3.0.0
matplotlib>=3.5.0
seaborn>=0.12.0
numpy>=1.21.0
mplcyberpunk>=0.7.0
ttkbootstrap>=1.10.0
```

---

## Troubleshooting

| Issue                     | Solution                                                       |
| ------------------------- | -------------------------------------------------------------- |
| "Failed to load data"     | Ensure `gdp_with_continent_filled.xlsx` is in the project root |
| Visualization not showing | Click "Clear Visualization" then re-analyze                    |
| Missing libraries         | `pip install -r requirements.txt`                              |
| Slow with many countries  | Reduce comparison to ≤10 countries                             |

---

**Version**: 2.0
**Last Updated**: March 2026
