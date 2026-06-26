"""Shared package for repo-local health and disposition tooling."""

from __future__ import annotations

from importlib import import_module

__all__ = [
    "assemble_health_findings",
    "check_disposition_store_consistency",
    "check_ledger_staleness",
    "health_benchmark_adapter",
    "health_disposition_store",
    "migrate_health_disposition_jsonl",
    "migrate_health_disposition_store",
    "select_health_artifacts",
    "split_multilens_findings",
    "validate_health_loop_state",
]


def __getattr__(name: str):
    if name not in __all__:
        raise AttributeError(name)
    return import_module(f"{__name__}.{name}")
