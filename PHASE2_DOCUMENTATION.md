# Phase 2 — Modular Orchestration & Dependency Inversion

## Architecture Overview

The application is decomposed into four logical packages following the
Dependency Inversion Principle (DIP). The **Core** module owns all
contracts; external modules depend on those contracts, never the reverse.

```
proj/
├── main.py                  # Orchestrator  (Part 5)
├── config.json              # Runtime configuration & driver selection
├── core/
│   ├── __init__.py          # Re-exports: DataSink, PipelineService, DataRecord
│   ├── contracts.py         # Protocol definitions (the "Boss")
│   └── engine.py            # TransformationEngine (business logic)
├── plugins/
│   ├── __init__.py
│   ├── inputs.py            # CsvReader, JsonReader, ExcelReader  (Part 3)
│   └── outputs.py           # ConsoleWriter, GraphicsChartWriter  (Part 4)
└── data/
    ├── __init__.py
    └── gdp_with_continent_filled.xlsx
```

---

## 1 `core/contracts.py` — Protocol Definitions

All protocols use `typing.Protocol` with `@runtime_checkable` for
structural (duck) typing. Any class matching the method signatures is
automatically compatible — no inheritance required.

### `DataRecord`

Structural type for a single GDP row.

| Property       | Type              | Description                      |
| -------------- | ----------------- | -------------------------------- |
| `country_name` | `str`             | Name of the country              |
| `continent`    | `str`             | Continent the country belongs to |
| `gdp_values`   | `Dict[int,float]` | Year → GDP value mapping         |

### `DataSink` (Outbound Abstraction)

Owned by Core, implemented by Output plugins. The Core calls these
methods to emit processed results — it never imports a concrete writer.

| Method          | Signature                                                                      | Purpose                    |
| --------------- | ------------------------------------------------------------------------------ | -------------------------- |
| `write`         | `(records: List[Dict], title: str = "") -> None`                               | Emit a list of result rows |
| `write_chart`   | `(chart_type: str, data: Dict, title: str = "", options: Dict = None) -> None` | Emit a visualization       |
| `write_summary` | `(summary: Dict, title: str = "") -> None`                                     | Emit a statistical summary |

Supported `chart_type` values: `bar`, `line`, `pie`, `grouped_bar`, `heatmap`.

### `PipelineService` (Inbound Abstraction)

Owned by Core, called by Input plugins. The Input module pushes raw
data through this interface without knowing the Core's internals.

| Method                   | Signature                                                    | Purpose                             |
| ------------------------ | ------------------------------------------------------------ | ----------------------------------- |
| `execute`                | `(raw_data: List[Dict]) -> None`                             | Ingest raw rows & run full pipeline |
| `get_available_analyses` | `() -> List[str]`                                            | List registered analysis names      |
| `run_analysis`           | `(analysis_name: str, params: Dict) -> Optional[List[Dict]]` | Run a single named analysis         |

Expected minimum keys in each `raw_data` dict:

- `'Country Name'` : `str`
- `'Continent'` : `str`
- Integer year keys mapping to GDP float values

---

## 2 `core/engine.py` — TransformationEngine

The engine is the domain's central class. It satisfies the
`PipelineService` protocol via structural typing — no explicit
`class TransformationEngine(PipelineService)` needed.

### Construction

```python
engine = TransformationEngine(sink=<DataSink>, config=<dict>)
```

| Parameter | Type       | Description                                      |
| --------- | ---------- | ------------------------------------------------ | -------------------------------------------------- |
| `sink`    | `DataSink` | Injected output target (console, chart, file, …) |
| `config`  | `dict      | None`                                            | Full application config including `pipeline` block |

The engine **never** imports a concrete writer class.

### Internal Dispatch

Analysis names are mapped to private methods via a dictionary-based
dispatch table (`self._dispatch`). This avoids if/elif chains and
makes registration data-driven.

### Registered Analyses

All iteration uses `map`, `filter`, `reduce`, `sorted` — no `for` or
`while` loops (FP compliance carried over from Phase 1).

| #   | Key                         | Description                                             | Required Params              |
| --- | --------------------------- | ------------------------------------------------------- | ---------------------------- |
| 1   | `top_countries`             | Top N countries by GDP for a continent & year           | `continent`, `year`, `top_n` |
| 2   | `bottom_countries`          | Bottom N countries by GDP for a continent & year        | `continent`, `year`, `top_n` |
| 3   | `growth_rate`               | GDP growth % per country in a continent over date range | `continent`, `date_range`    |
| 4   | `avg_gdp_by_continent`      | Average GDP by continent for a date range               | `date_range`                 |
| 5   | `global_gdp_trend`          | Total world GDP per year across date range              | `date_range`                 |
| 6   | `fastest_growing_continent` | Continents ranked by GDP growth over date range         | `date_range`                 |
| 7   | `consistent_decline`        | Countries with consecutive GDP decline in last X years  | `decline_years`              |
| 8   | `continent_contribution`    | Each continent's share of total global GDP              | `date_range`                 |

### Parameter Defaults

| Param           | Default        |
| --------------- | -------------- |
| `continent`     | `"Asia"`       |
| `year`          | last available |
| `date_range`    | `[2000, 2020]` |
| `top_n`         | `10`           |
| `decline_years` | `5`            |

### Result Format

Every analysis returns `List[Dict[str, Any]]`. Common keys per analysis:

**top_countries / bottom_countries**

```json
{
  "rank": 1,
  "country": "China",
  "continent": "Asia",
  "year": 2020,
  "gdp": 1.47e13
}
```

**growth_rate**

```json
{"country": "China", "continent": "Asia", "start_year": 2000, "end_year": 2020, "start_gdp": ..., "end_gdp": ..., "growth_pct": 1042.56}
```

**avg_gdp_by_continent**

```json
{
  "continent": "Europe",
  "avg_gdp": 1.23e11,
  "start_year": 2000,
  "end_year": 2020,
  "country_count": 45
}
```

**global_gdp_trend**

```json
{ "year": 2005, "total_gdp": 4.72e13, "country_count": 200 }
```

**fastest_growing_continent**

```json
{"continent": "Asia", "start_year": 2000, "end_year": 2020, "start_gdp": ..., "end_gdp": ..., "growth_pct": 312.45}
```

**consistent_decline**

```json
{"country": "...", "continent": "...", "decline_years": 5, "start_year": 2018, "end_year": 2022, "start_gdp": ..., "end_gdp": ..., "decline_pct": -12.34}
```

**continent_contribution**

```json
{"continent": "North America", "total_gdp": ..., "global_total_gdp": ..., "contribution_pct": 28.5, "start_year": 2000, "end_year": 2020}
```

### Helper Functions (module-level)

| Function           | Purpose                                               |
| ------------------ | ----------------------------------------------------- |
| `_safe_div(n, d)`  | Division returning `0.0` when denominator is zero     |
| `_year_keys(row)`  | Extract sorted integer keys from a dict               |
| `_raw_to_df(data)` | Convert `List[Dict]` → `pd.DataFrame`                 |
| `_resolve_years`   | Filter DataFrame year columns within a `[start, end]` |
| `_continent_df`    | Filter DataFrame rows for a single continent          |
| `_all_continents`  | Return sorted unique continent names from a DataFrame |

---

## 3 `config.json` — Pipeline Configuration

### `pipeline` block

```json
{
  "pipeline": {
    "input_driver": "excel",
    "output_driver": "console",
    "data_source": "data/gdp_with_continent_filled.xlsx",
    "analyses": ["top_countries", "bottom_countries", ...],
    "default_params": {
      "continent": "Asia",
      "year": 2020,
      "date_range": [2000, 2020],
      "top_n": 10,
      "decline_years": 5
    }
  }
}
```

| Key              | Type   | Description                                         |
| ---------------- | ------ | --------------------------------------------------- |
| `input_driver`   | `str`  | Key into `input_drivers` map (`csv`/`json`/`excel`) |
| `output_driver`  | `str`  | Key into `output_drivers` map (`console`/`chart`)   |
| `data_source`    | `str`  | Path to the data file (relative to project root)    |
| `analyses`       | `list` | Ordered list of analyses to execute                 |
| `default_params` | `dict` | Default parameters passed to every analysis         |

### `input_drivers` / `output_drivers` maps

```json
{
  "input_drivers": {
    "csv": { "class": "CsvReader", "module": "plugins.inputs" },
    "json": { "class": "JsonReader", "module": "plugins.inputs" },
    "excel": { "class": "ExcelReader", "module": "plugins.inputs" }
  },
  "output_drivers": {
    "console": { "class": "ConsoleWriter", "module": "plugins.outputs" },
    "chart": { "class": "GraphicsChartWriter", "module": "plugins.outputs" }
  }
}
```

Swapping IO implementations requires only changing `input_driver` /
`output_driver` in the config — no code modifications needed.

---

## 4 Dependency Flow

```
Input (plugins.inputs)           Core (core)              Output (plugins.outputs)
  │                                │                           │
  │  reads file, calls             │                           │
  │  PipelineService.execute() ──►│                           │
  │                                │  transforms data          │
  │                                │  calls DataSink.write() ─►│
  │                                │                           │  renders output
```

**Golden Rules enforced:**

1. **Inbound Abstraction** — Input depends on `PipelineService` (from Core), never on `TransformationEngine` directly.
2. **Outbound Abstraction** — Core depends on `DataSink` (defined in Core), never imports a concrete writer.
3. **Ownership** — Core defines all contracts; plugins merely implement their shapes.

---

## 5 FP Compliance

All modules maintain the Phase 1 functional programming constraint:

- Zero `for` / `while` loops
- Iteration via `map()`, `filter()`, `reduce()`, `sorted()`, `zip()`, `all()`, `any()`
- Lambdas for inline transformations
- `functools.reduce` for accumulation
