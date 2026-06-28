#!/usr/bin/env python3
"""Compatibility wrapper for the packaged disposition-store consistency checker."""

from importlib import import_module

from _compat_entrypoint import resolve_module_name, run_module_entrypoint

_module = import_module(
    resolve_module_name("al_dev_tools.health.check_disposition_store_consistency")
)
globals().update(
    {name: value for name, value in _module.__dict__.items() if not name.startswith("_")}
)


if __name__ == "__main__":
    raise SystemExit(
        run_module_entrypoint("al_dev_tools.health.check_disposition_store_consistency")
    )
