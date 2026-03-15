"""Process orchestration entry point for the Phase 3 pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from multiprocessing import Manager, Process, Queue, Value
from time import sleep
from typing import Any, Dict

from phase3 import get_phase3_config
from phase3.core_module import StatefulAggregator, StatelessVerifier
from phase3.input_module import InputModule, SENTINEL, build_input_config
from phase3.output_module import OutputModule, OutputModuleConfig
from phase3.telemetry import PipelineTelemetry


@dataclass(frozen=True)
class OrchestratorConfig:
    """Queue sizing and runtime settings for process orchestration."""

    raw_queue_max_size: int
    processed_queue_max_size: int
    output_queue_max_size: int
    core_parallelism: int
    telemetry_poll_seconds: float
    output_refresh_seconds: float


class _TelemetryCollector:
    """Collects telemetry snapshots published by the telemetry subject."""

    def __init__(self, snapshots: list) -> None:
        self._snapshots = snapshots

    def on_telemetry_update(self, snapshot: Dict[str, Any]) -> None:
        self._snapshots.append(snapshot)


def _run_input_stage(config: Dict[str, Any], raw_queue: Queue, num_workers: int) -> None:
    """Runs the producer stage in its own process."""
    input_cfg = build_input_config(config)
    InputModule(input_cfg, raw_queue, num_workers).run()


def _run_verifier_worker(
    config: Dict[str, Any],
    raw_queue: Queue,
    processed_queue: Queue,
    seen_counter: Value,
    dropped_counter: Value,
) -> None:
    """Runs one stateless verifier worker process."""
    p3 = get_phase3_config(config)
    verifier = StatelessVerifier(p3.get("processing", {}).get("stateless_tasks", {}))

    while True:
        packet = raw_queue.get()
        if packet is SENTINEL:
            processed_queue.put(SENTINEL)
            break

        with seen_counter.get_lock():
            seen_counter.value += 1

        verified = verifier.process(packet)
        if verified is None:
            with dropped_counter.get_lock():
                dropped_counter.value += 1
            continue

        processed_queue.put(verified)


def _run_aggregator_stage(
    config: Dict[str, Any],
    processed_queue: Queue,
    output_queue: Queue,
    worker_count: int,
    verified_counter: Value,
) -> None:
    """Runs the stateful aggregator stage until all workers send sentinels."""
    p3 = get_phase3_config(config)
    aggregator = StatefulAggregator(p3.get("processing", {}).get("stateful_tasks", {}))

    done_workers = 0
    while done_workers < worker_count:
        packet = processed_queue.get()
        if packet is SENTINEL:
            done_workers += 1
            continue

        aggregated = aggregator.process(packet)
        output_queue.put(aggregated)
        with verified_counter.get_lock():
            verified_counter.value += 1

    output_queue.put(SENTINEL)


def _run_output_stage(
    config: Dict[str, Any],
    output_queue: Queue,
    output_results: Any,
    output_state: Any,
) -> None:
    """Runs the output consumer stage in its own process."""
    p3 = get_phase3_config(config)
    runtime = {
        "processed_queue": output_queue,
        "worker_count": 1,
        "results": output_results,
        "state": output_state,
    }
    output_cfg = OutputModuleConfig(
        refresh_interval_seconds=float(
            p3.get("pipeline_dynamics", {}).get("output_refresh_seconds", 0.0)
        )
    )
    OutputModule(output_cfg, runtime).run()


class PipelineOrchestrator:
    """Coordinates producer, workers, aggregator, telemetry, and output processes."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Stores raw orchestrator configuration."""
        self.config = config
        self.last_run: Dict[str, Any] = {}

    def _build_runtime_config(self) -> OrchestratorConfig:
        """Builds typed orchestration settings from config."""
        p3 = get_phase3_config(self.config)
        dynamics = p3.get("pipeline_dynamics", {})
        queue_size = int(dynamics.get("stream_queue_max_size", 50))
        return OrchestratorConfig(
            raw_queue_max_size=queue_size,
            processed_queue_max_size=queue_size,
            output_queue_max_size=queue_size,
            core_parallelism=int(dynamics.get("core_parallelism", 4)),
            telemetry_poll_seconds=float(dynamics.get("telemetry_poll_seconds", 0.05)),
            output_refresh_seconds=float(dynamics.get("output_refresh_seconds", 0.0)),
        )

    def start(self) -> Dict[str, Any]:
        """Creates queues, starts processes, and returns runtime handles."""
        runtime_cfg = self._build_runtime_config()

        raw_queue = Queue(maxsize=runtime_cfg.raw_queue_max_size)
        processed_queue = Queue(maxsize=runtime_cfg.processed_queue_max_size)
        output_queue = Queue(maxsize=runtime_cfg.output_queue_max_size)

        manager = Manager()
        output_results = manager.list()
        output_state = manager.dict({"consumed": 0, "completed": False, "last_packet": None})
        seen_counter = Value("i", 0)
        dropped_counter = Value("i", 0)
        verified_counter = Value("i", 0)

        telemetry_snapshots: list = []
        telemetry = PipelineTelemetry({
            "raw_stream": raw_queue,
            "processed_stream": processed_queue,
            "output_stream": output_queue,
        })
        telemetry.subscribe(_TelemetryCollector(telemetry_snapshots))

        processes = [
            Process(
                target=_run_input_stage,
                args=(self.config, raw_queue, runtime_cfg.core_parallelism),
                name="p3-input",
            )
        ]

        for idx in range(runtime_cfg.core_parallelism):
            processes.append(
                Process(
                    target=_run_verifier_worker,
                    args=(self.config, raw_queue, processed_queue, seen_counter, dropped_counter),
                    name=f"p3-verify-{idx + 1}",
                )
            )

        processes.append(
            Process(
                target=_run_aggregator_stage,
                args=(self.config, processed_queue, output_queue, runtime_cfg.core_parallelism, verified_counter),
                name="p3-aggregator",
            )
        )
        processes.append(
            Process(
                target=_run_output_stage,
                args=(self.config, output_queue, output_results, output_state),
                name="p3-output",
            )
        )

        for proc in processes:
            proc.start()

        return {
            "config": runtime_cfg,
            "manager": manager,
            "raw_queue": raw_queue,
            "processed_queue": processed_queue,
            "output_queue": output_queue,
            "processes": processes,
            "seen_counter": seen_counter,
            "dropped_counter": dropped_counter,
            "verified_counter": verified_counter,
            "output_results": output_results,
            "output_state": output_state,
            "telemetry": telemetry,
            "telemetry_snapshots": telemetry_snapshots,
        }

    def is_running(self, runtime: Dict[str, Any]) -> bool:
        """Returns True while any worker process is still alive."""
        return any(proc.is_alive() for proc in runtime["processes"])

    def poll(self, runtime: Dict[str, Any]) -> Dict[str, Any]:
        """Polls one live telemetry snapshot from the active queues."""
        return runtime["telemetry"].poll_once()

    def stop(self, runtime: Dict[str, Any]) -> None:
        """Terminates any still-running pipeline processes."""
        for proc in runtime["processes"]:
            if proc.is_alive():
                proc.terminate()
        for proc in runtime["processes"]:
            proc.join()

    def finalize(self, runtime: Dict[str, Any]) -> Dict[str, Any]:
        """Joins processes and builds the final run summary."""
        for proc in runtime["processes"]:
            proc.join()

        packets = list(runtime["output_results"])
        final_avg = packets[-1].get("computed_metric") if packets else None
        output_state = dict(runtime["output_state"])

        self.last_run = {
            "packets_seen": runtime["seen_counter"].value,
            "verified": runtime["verified_counter"].value,
            "dropped": runtime["dropped_counter"].value,
            "final_average": final_avg,
            "results": packets,
            "telemetry": list(runtime["telemetry_snapshots"]),
            "output": output_state,
        }
        runtime["manager"].shutdown()
        return self.last_run

    def run(self) -> None:
        """Builds queues, starts worker processes, polls telemetry, and prints a summary."""
        runtime = self.start()

        try:
            while self.is_running(runtime):
                self.poll(runtime)
                sleep(runtime["config"].telemetry_poll_seconds)
        finally:
            for proc in runtime["processes"]:
                if proc.is_alive():
                    proc.terminate()
                    proc.join()

        summary = self.finalize(runtime)

        print("Phase 3 pipeline complete.")
        print(f"Packets seen: {summary['packets_seen']}")
        print(f"Verified:     {summary['verified']}")
        print(f"Dropped:      {summary['dropped']}")
        print(f"Final avg:    {summary['final_average'] if summary['final_average'] is not None else 'N/A'}")
