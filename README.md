# GDP Analysis Dashboard

Interactive GDP analysis dashboard built with Streamlit, Plotly, and a plugin-based engine architecture.

## Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt`

## Setup

```bash
cd proj
pip install -r requirements.txt
```

## How to Run

### Dashboard (Streamlit GUI)

```bash
python main.py
```

Or directly:

```bash
python -m streamlit run gdp_dashboard_streamlit.py --server.headless true --theme.base dark
```

Opens at `http://localhost:8501`.

### CLI Mode (Console Output)

Run all analyses:

```bash
python main.py --cli
```

Run a single analysis:

```bash
python main.py top_countries
python main.py growth_rate
python main.py avg_gdp_by_continent
```

List available analyses:

```bash
python main.py --list
```

### Build Standalone Executable

```bash
pip install pyinstaller
python build_exe.py
```

Output: `dist/GDP_Dashboard/GDP_Dashboard.exe`

## Project Structure

```
proj/
  main.py                       Entry point (GUI / CLI)
  gdp_dashboard_streamlit.py    Streamlit dashboard app
  data_loader.py                Data loading and validation
  data_processor.py             GDP calculations and statistics
  config.json                   Configuration (data paths, analyses, UI settings)
  gdp_with_continent_filled.xlsx  GDP dataset
  run_dashboard.py              Desktop app launcher (used by PyInstaller)
  build_exe.py                  PyInstaller build script
  requirements.txt              Python dependencies
  core/
    contracts.py                Protocol interfaces (DataSink, PipelineService)
    engine.py                   Transformation engine (Phase 2 analyses)
  plugins/
    inputs.py                   Input readers (CSV, JSON, Excel)
    outputs.py                  Output sinks (Console, Chart PNG, Streamlit, Tkinter)
```

## Configuration

Edit `config.json` to change:

- `pipeline.data_source` — path to data file (xlsx/csv/json)
- `pipeline.output_driver` — `"console"`, `"chart"`, or `"streamlit"`
- `pipeline.analyses` — list of analyses to run in CLI mode
- `pipeline.default_params` — default continent, year, top_n, etc.

## Available Analyses

**Dashboard (Phase 1):** Country GDP Trend, Compare Countries, Continent Analysis, Top Countries, GDP Growth Rate, Statistical Summary, Year Comparison, Correlation Analysis, Regional Analysis, Year Analysis, Complete Analysis

**Engine (Phase 2):** Top Countries, Bottom Countries, Growth Rate, Avg GDP by Continent, Global GDP Trend, Fastest Growing Continent, Consistent Decline, Continent Contribution
