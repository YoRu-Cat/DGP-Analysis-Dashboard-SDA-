# Core Module - The Domain
# Contains business logic, transformation rules, and Protocol definitions.
# This module is the authority — it defines the contracts that other modules must satisfy.

from core.contracts import DataSink, PipelineService, DataRecord

__all__ = ['DataSink', 'PipelineService', 'DataRecord']
