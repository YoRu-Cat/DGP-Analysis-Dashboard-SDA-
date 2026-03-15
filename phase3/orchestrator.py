"""Process orchestration entry point for the Phase 3 pipeline."""

from __future__ import annotations

from multiprocessing import Manager, Process, Queue, Value
from dataclasses import dataclass
from typing import Dict, Any

from phase3.core_module import StatelessVerifier, StatefulAggregator
from phase3.input_module import InputModule, build_input_config, SENTINEL


@dataclass(frozen=True)
class OrchestratorConfig:
    """Queue sizing configuration for process orchestration."""

    raw_queue_max_size: int
    processed_queue_max_size: int
    core_parallelism: int


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
    verifier = StatelessVerifier(config.get("phase3", {}).get("processing", {}).get("stateless_tasks", {}))

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
    worker_count: int,
    output_packets: Any,
    verified_counter: Value,
) -> None:
    """Runs the stateful aggregator stage until all workers send sentinels."""
    aggregator = StatefulAggregator(config.get("phase3", {}).get("processing", {}).get("stateful_tasks", {}))

    done_workers = 0
    while done_workers < worker_count:
        packet = processed_queue.get()
        if packet is SENTINEL:
            done_workers += 1
            continue

        aggregated = aggregator.process(packet)
        output_packets.append(aggregated)
        with verified_counter.get_lock():
            verified_counter.value += 1


class PipelineOrchestrator:
    """Coordinates producer, workers, aggregator, and output processes."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Stores raw orchestrator configuration."""
        self.config = config
        self.last_run: Dict[str, Any] = {}

    def _build_runtime_config(self) -> OrchestratorConfig:
        """Builds typed orchestration settings from config."""
        p3 = self.config.get("phase3", {})
        dynamics = p3.get("pipeline_dynamics", {})
        queue_size = int(dynamics.get("stream_queue_max_size", 50))
        return OrchestratorConfig(
            raw_queue_max_size=queue_size,
            processed_queue_max_size=queue_size,
            core_parallelism=int(dynamics.get("core_parallelism", 4)),
        )

    def run(self) -> None:
        """Builds queues, starts worker processes, and manages lifecycle."""
        runtime_cfg = self._build_runtime_config()

        raw_queue = Queue(maxsize=runtime_cfg.raw_queue_max_size)
        processed_queue = Queue(maxsize=runtime_cfg.processed_queue_max_size)

        manager = Manager()
        output_packets = manager.list()

        seen_counter = Value("i", 0)
        dropped_counter = Value("i", 0)
        verified_counter = Value("i", 0)

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
                args=(self.config, processed_queue, runtime_cfg.core_parallelism, output_packets, verified_counter),
                name="p3-aggregator",
            )
        )

        try:
            for proc in processes:
                proc.start()

            for proc in processes:
                proc.join()
        finally:
            for proc in processes:
                if proc.is_alive():
                    proc.terminate()
                    proc.join()

        packets = list(output_packets)
        final_avg = packets[-1].get("computed_metric") if packets else None

        self.last_run = {
            "packets_seen": seen_counter.value,
            "verified": verified_counter.value,
            "dropped": dropped_counter.value,
            "final_average": final_avg,
            "results": packets,
        }

        print("Phase 3 pipeline complete.")
        print(f"Packets seen: {seen_counter.value}")
        print(f"Verified:     {verified_counter.value}")
        print(f"Dropped:      {dropped_counter.value}")
        print(f"Final avg:    {final_avg if final_avg is not None else 'N/A'}")
