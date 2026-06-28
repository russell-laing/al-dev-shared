#!/usr/bin/env python3
"""Compatibility wrapper for the packaged health disposition store CLI."""

from importlib import import_module

from _compat_entrypoint import resolve_module_name, run_module_entrypoint

_module = import_module(
    resolve_module_name("al_dev_tools.health.health_disposition_store")
)
globals().update(
    {name: value for name, value in _module.__dict__.items() if not name.startswith("_")}
)
_cli_match = _module._cli_match  # noqa: SLF001


if __name__ == "__main__":
    raise SystemExit(
        run_module_entrypoint("al_dev_tools.health.health_disposition_store")
    )
