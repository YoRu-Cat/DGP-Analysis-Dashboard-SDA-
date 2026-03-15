from __future__ import annotations

from typing import Dict, Any
from functools import reduce
import json
import sys
import importlib
from multiprocessing import Manager, Process, Queue, Value
from time import sleep


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
    import subprocess, os, socket, time, webbrowser

    script_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(script_dir, 'gdp_dashboard_streamlit.py')
    port = 8501

    st_dir = os.path.join(script_dir, '.streamlit')
    os.makedirs(st_dir, exist_ok=True)
    cred = os.path.join(st_dir, 'credentials.toml')
    if not os.path.exists(cred):
        open(cred, 'w').write('[general]\nemail = ""\n')
    cfg_toml = os.path.join(st_dir, 'config.toml')
    if not os.path.exists(cfg_toml):
        open(cfg_toml, 'w').write(
            '[server]\nheadless = true\n'
            f'port = {port}\nenableCORS = false\nenableXsrfProtection = false\n\n'
            '[browser]\ngatherUsageStats = false\n'
            f'serverAddress = "localhost"\nserverPort = {port}\n\n'
            '[global]\ndevelopmentMode = false\n'
        )

    proc = subprocess.Popen(
        [
            sys.executable, '-m', 'streamlit', 'run', app_path,
            '--server.headless=true',
            f'--server.port={port}',
            '--browser.gatherUsageStats=false',
            '--global.developmentMode=false',
        ],
        cwd=script_dir,
    )

    deadline = time.time() + 30
    ready = False
    while time.time() < deadline:
        try:
            with socket.create_connection(('127.0.0.1', port), timeout=1):
                ready = True
                break
        except OSError:
            time.sleep(0.3)

    if not ready:
        print('ERROR: Streamlit server did not start in time.')
        proc.terminate()
        return

    url = f'http://localhost:{port}'

    _BROWSERS = [
        r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Microsoft\Edge\Application\msedge.exe',
        r'C:\Program Files\Google\Chrome\Application\chrome.exe',
        r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
    ]
    browser_path = next((b for b in _BROWSERS if os.path.isfile(b)), None)

    if browser_path:
        app_proc = subprocess.Popen([
            browser_path,
            f'--app={url}',
            '--window-size=1600,900',
            '--disable-extensions',
            '--new-window',
        ])
        app_proc.wait()
    else:
        webbrowser.open(url)
        proc.wait()


def _print_usage() -> None:
    print("Usage:")
    print("  python main.py                        Launch Streamlit dashboard (default)")
    print("  python main.py --gui                  Launch Streamlit dashboard")
    print("  python main.py --cli                  Run full GDP pipeline in console")
    print("  python main.py --phase3               Run Phase 3 concurrent pipeline (console)")
    print("  python main.py <analysis_name>        Run a single analysis (console)")
    print("  python main.py --list                 List available analyses")
    print()
    print("Output driver is set in config.json -> pipeline.output_driver")
    print("  'console'  -> formatted text to stdout")
    print("  'chart'    -> PNG files to output_charts/")
    print("  'streamlit'-> render inside Streamlit dashboard")


def run_phase3_from_main(config_path: str = 'config.json') -> None:
    """Runs Phase 3 with main.py explicitly orchestrating queues and processes."""
    from phase3 import get_phase3_config
    from phase3.orchestrator import (
        _TelemetryCollector,
        _run_aggregator_stage,
        _run_input_stage,
        _run_output_stage,
        _run_verifier_worker,
    )
    from phase3.telemetry import PipelineTelemetry

    cfg = _load_config(config_path)
    p3 = get_phase3_config(cfg)
    dynamics = p3.get('pipeline_dynamics', {})

    queue_size = int(dynamics.get('stream_queue_max_size', 50))
    core_parallelism = int(dynamics.get('core_parallelism', 4))
    telemetry_poll_seconds = float(dynamics.get('telemetry_poll_seconds', 0.05))

    raw_queue = Queue(maxsize=queue_size)
    processed_queue = Queue(maxsize=queue_size)
    output_queue = Queue(maxsize=queue_size)

    manager = Manager()
    output_results = manager.list()
    output_state = manager.dict({'consumed': 0, 'completed': False, 'last_packet': None})
    seen_counter = Value('i', 0)
    dropped_counter = Value('i', 0)
    verified_counter = Value('i', 0)

    telemetry_snapshots: list = []
    telemetry = PipelineTelemetry({
        'raw_stream': raw_queue,
        'processed_stream': processed_queue,
        'output_stream': output_queue,
    })
    telemetry.subscribe(_TelemetryCollector(telemetry_snapshots))

    processes = [
        Process(
            target=_run_input_stage,
            args=(cfg, raw_queue, core_parallelism),
            name='p3-input',
        )
    ]

    for idx in range(core_parallelism):
        processes.append(
            Process(
                target=_run_verifier_worker,
                args=(cfg, raw_queue, processed_queue, seen_counter, dropped_counter),
                name=f'p3-verify-{idx + 1}',
            )
        )

    processes.append(
        Process(
            target=_run_aggregator_stage,
            args=(cfg, processed_queue, output_queue, core_parallelism, verified_counter),
            name='p3-aggregator',
        )
    )
    processes.append(
        Process(
            target=_run_output_stage,
            args=(cfg, output_queue, output_results, output_state),
            name='p3-output',
        )
    )

    for proc in processes:
        proc.start()

    try:
        while any(proc.is_alive() for proc in processes):
            telemetry.poll_once()
            sleep(telemetry_poll_seconds)
    finally:
        for proc in processes:
            if proc.is_alive():
                proc.terminate()
        for proc in processes:
            proc.join()

    packets = list(output_results)
    final_avg = packets[-1].get('computed_metric') if packets else None
    summary = {
        'packets_seen': seen_counter.value,
        'verified': verified_counter.value,
        'dropped': dropped_counter.value,
        'final_average': final_avg,
        'results': packets,
        'telemetry': list(telemetry_snapshots),
        'output': dict(output_state),
    }

    manager.shutdown()

    print('Phase 3 pipeline complete.')
    print(f"Packets seen: {summary['packets_seen']}")
    print(f"Verified:     {summary['verified']}")
    print(f"Dropped:      {summary['dropped']}")
    print(f"Final avg:    {summary['final_average'] if summary['final_average'] is not None else 'N/A'}")


if __name__ == '__main__':
    import multiprocessing
    multiprocessing.freeze_support()

    args = sys.argv[1:]

    if not args or args[0] == '--gui':
        run_gui()
    elif args[0] == '--cli':
        run_pipeline()
    elif args[0] == '--phase3':
        run_phase3_from_main()
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

