"""Shared helpers for top-level compatibility entrypoints."""

from __future__ import annotations

import runpy
from importlib import import_module
from typing import Callable


def resolve_module_name(packaged: str) -> str:
    try:
        import_module(f"scripts.{packaged}")
    except ModuleNotFoundError:
        return packaged
    return f"scripts.{packaged}"


def run_module_entrypoint(packaged: str) -> int:
    runpy.run_module(resolve_module_name(packaged), run_name="__main__")
    return 0


def run_main_entrypoint(packaged: str) -> int:
    module = import_module(resolve_module_name(packaged))
    main: Callable[[], int | None] = getattr(module, "main")
    result = main()
    return 0 if result is None else int(result)
