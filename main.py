from __future__ import annotations

from typing import Dict, Any
from functools import reduce
import json
import sys
import importlib


_load_config = lambda path: json.loads(
    open(path, 'r', encoding='utf-8').read()
)


def _resolve_class(driver_entry: Dict[str, str]) -> type:
    module = importlib.import_module(driver_entry['module'])
    return getattr(module, driver_entry['class'])


def _build_driver_map(cfg: Dict[str, Any], section: str) -> Dict[str, type]:
    entries = cfg.get(section, {})
    return dict(map(
        lambda kv: (kv[0], _resolve_class(kv[1])),
        entries.items(),
    ))


def _create_input(input_drivers: Dict[str, type], driver_name: str, data_source: str):
    cls = input_drivers.get(driver_name)
    if cls is None:
        raise ValueError(f"Unknown input driver: {driver_name}")
    return cls(file_path=data_source)


def _create_output(output_drivers: Dict[str, type], driver_name: str, cfg: Dict[str, Any]):
    cls = output_drivers.get(driver_name)
    if cls is None:
        raise ValueError(f"Unknown output driver: {driver_name}")
    return cls(config=cfg)


def run_pipeline(config_path: str = 'config.json') -> None:
    cfg = _load_config(config_path)
    pipeline = cfg.get('pipeline', {})

    input_driver_name = pipeline.get('input_driver', 'excel')
    output_driver_name = pipeline.get('output_driver', 'console')
    data_source = pipeline.get('data_source', 'gdp_with_continent_filled.xlsx')

    input_drivers = _build_driver_map(cfg, 'input_drivers')
    output_drivers = _build_driver_map(cfg, 'output_drivers')

    sink = _create_output(output_drivers, output_driver_name, cfg)
    reader = _create_input(input_drivers, input_driver_name, data_source)

    from core.engine import TransformationEngine
    engine = TransformationEngine(sink, cfg)

    print(f"Pipeline: {input_driver_name} -> engine -> {output_driver_name}")
    print(f"Data source: {data_source}")
    print(f"Analyses: {', '.join(pipeline.get('analyses', []))}")
    print()

    reader.read_and_push(engine)

    print("\nPipeline complete.")


def run_single(analysis_name: str, config_path: str = 'config.json') -> None:
    cfg = _load_config(config_path)
    pipeline = cfg.get('pipeline', {})

    input_driver_name = pipeline.get('input_driver', 'excel')
    output_driver_name = pipeline.get('output_driver', 'console')
    data_source = pipeline.get('data_source', 'gdp_with_continent_filled.xlsx')

    input_drivers = _build_driver_map(cfg, 'input_drivers')
    output_drivers = _build_driver_map(cfg, 'output_drivers')

    sink = _create_output(output_drivers, output_driver_name, cfg)
    reader = _create_input(input_drivers, input_driver_name, data_source)

    cfg_single = {
        **cfg,
        'pipeline': {**pipeline, 'analyses': []},
    }

    from core.engine import TransformationEngine
    engine = TransformationEngine(sink, cfg_single)

    reader.read_and_push(engine)

    params = pipeline.get('default_params', {})
    results = engine.run_analysis(analysis_name, params)

    if results is None:
        print(f"Unknown analysis: {analysis_name}")
        print(f"Available: {', '.join(engine.get_available_analyses())}")
        return

    title = analysis_name.replace('_', ' ').title()
    sink.write(results, title=title)


def run_gui() -> None:
    import subprocess, os
    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, 'gdp_dashboard_streamlit.py')
    subprocess.run(
        [sys.executable, '-m', 'streamlit', 'run', app_path,
         '--server.headless=true', '--theme.base=dark',
         '--theme.primaryColor=#1d9bf0',
         '--theme.backgroundColor=#0a0a0a',
         '--theme.secondaryBackgroundColor=#111111',
         '--theme.textColor=#e7e9ea'],
        cwd=script_dir,
    )


def _print_usage() -> None:
    print("Usage:")
    print("  python main.py                        Launch Streamlit dashboard (default)")
    print("  python main.py --gui                  Launch Streamlit dashboard")
    print("  python main.py --cli                  Run full pipeline in console")
    print("  python main.py <analysis_name>        Run a single analysis (console)")
    print("  python main.py --list                 List available analyses")
    print()
    print("Output driver is set in config.json -> pipeline.output_driver")
    print("  'console'  -> formatted text to stdout")
    print("  'chart'    -> PNG files to output_charts/")
    print("  'streamlit'-> render inside Streamlit dashboard")


if __name__ == '__main__':
    args = sys.argv[1:]

    if not args or args[0] == '--gui':
        run_gui()
    elif args[0] == '--cli':
        run_pipeline()
    elif args[0] == '--list':
        from core.engine import TransformationEngine
        print("Available analyses:")
        list(map(
            lambda name: print(f"  - {name}"),
            TransformationEngine._ANALYSES,
        ))
    elif args[0] == '--help' or args[0] == '-h':
        _print_usage()
    else:
        run_single(args[0])

