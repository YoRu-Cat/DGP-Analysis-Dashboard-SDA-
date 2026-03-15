# Phase 3 Pipeline Documentation

## Overview

Phase 3 implements a generic packet pipeline with three main stages:

1. Input stage: reads source rows and maps them to internal packet fields.
2. Core stage: verifies packet authenticity and computes stateful metrics.
3. Output stage: consumes processed packets and publishes updates.

The package is designed to support concurrent execution with bounded queues and telemetry-based backpressure visibility.

## Module Reference

### `phase3/__init__.py`

Exports the package namespace and identifies `phase3` as the generic concurrent pipeline package.

### `phase3/contracts.py`

Defines protocol interfaces used by the pipeline:

1. `GenericInputModule`
2. `GenericCoreModule`
3. `GenericOutputModule`
4. `TelemetryObserver`
5. `PipelineTelemetrySubject`
6. `PacketProcessor`

### `phase3/input_module.py`

Input-side functionality:

1. `ColumnSchema`: maps source columns to internal packet keys and data types.
2. `InputModuleConfig`: typed input configuration.
3. `build_input_config(cfg)`: reads Phase 3 config and builds typed input config.
4. `SchemaMapper`: casts and maps one raw row to one internal packet.
5. `InputModule`: reads CSV rows, emits mapped packets to raw queue, then emits sentinels.

Key behavior:

1. Uses `_TYPE_CASTERS` for schema-driven type conversion.
2. Skips invalid rows by returning `None` from mapper.
3. Applies input delay from config to simulate stream pacing.

### `phase3/core_module.py`

Core processing workers:

1. `CoreModuleConfig`: worker-level config model.
2. `StatelessVerifier`: verifies packet signatures using PBKDF2-HMAC-SHA256.
3. `StatefulAggregator`: computes sliding-window average and appends `computed_metric`.

Key behavior:

1. Verifier returns `None` for invalid packets.
2. Aggregator maintains a deque window and outputs rounded averages.

### `phase3/telemetry.py`

Telemetry publisher for queue health:

1. `TelemetryThresholds`: defines `flowing_max` and `warning_max`.
2. `PipelineTelemetry`: observer-subject implementation with subscribe/unsubscribe/publish.
3. `poll_once()`: samples queue size, computes utilization, classifies health, and publishes a snapshot.

### `phase3/output_module.py`

Output-side consumer definitions:

1. `OutputModuleConfig`: output runtime settings.
2. `OutputModule`: consumes processed packets, stores results, and emits observer updates.

### `phase3/orchestrator.py`

Pipeline orchestration entry point:

1. `OrchestratorConfig`: queue sizing config.
2. `PipelineOrchestrator`: process coordinator for producer, workers, aggregator, and lifecycle management.

## Current Implementation Status

1. Part 1: scaffold package and interfaces - complete.
2. Part 2: config and main wiring - complete.
3. Part 3: input module - complete.
4. Part 4: stateless verifier - complete.
5. Part 5: stateful aggregator - complete.
6. Part 6: orchestrator - complete.
7. Part 7: telemetry `poll_once` - complete.
8. Part 8: output module `run` - complete.
9. Part 9: architecture/design artifact - complete.
10. Part 10: diagram artifact - complete.
11. Part 11: validation artifact - complete.
12. Part 12: final documentation pass - complete.

## Runtime Flow

1. `InputModule` pushes mapped packets into the raw queue.
2. Parallel verifier workers consume raw packets and emit verified packets.
3. Aggregator consumes verified packets and appends `computed_metric`.
4. Output module consumes aggregated packets, stores results, and emits final updates.
5. Telemetry captures queue utilization snapshots and notifies observers.

## Supporting Documents

1. Root architecture guide: `PHASE3_EXPLAINED.md`
2. Root diagram set: `PHASE3_DIAGRAMS.md`
3. Root validation report: `PHASE3_VALIDATION.md`
4. Root final handoff: `PHASE3_FINAL.md`
