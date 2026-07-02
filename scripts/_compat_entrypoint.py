"""Shared helpers for top-level compatibility entrypoints."""

from __future__ import annotations

import inspect
from importlib import import_module
import sys
from typing import Sequence


def resolve_module_name(packaged: str) -> str:
    try:
        import_module(f"scripts.{packaged}")
    except ModuleNotFoundError as e:
        missing = e.name
        if missing == "scripts" or missing == f"scripts.{packaged}":
            return packaged
        raise
    return f"scripts.{packaged}"


def _invoke_main(module, argv: Sequence[str] | None = None) -> int:
    main = getattr(module, "main")
    if argv is None:
        argv = sys.argv[1:]

    try:
        signature = inspect.signature(main)
    except (TypeError, ValueError):
        signature = None

    if signature is not None:
        var_positional = [
            param
            for param in signature.parameters.values()
            if param.kind == inspect.Parameter.VAR_POSITIONAL
        ]
        if var_positional:
            result = main(*argv)
        else:
            positional = [
                param
                for param in signature.parameters.values()
                if param.kind
                in (
                    inspect.Parameter.POSITIONAL_ONLY,
                    inspect.Parameter.POSITIONAL_OR_KEYWORD,
                )
            ]
            if not positional:
                result = main()
            else:
                result = main(list(argv))
    else:
        result = main(list(argv))

    return 0 if result is None else int(result)


def run_module_entrypoint(packaged: str, argv: Sequence[str] | None = None) -> int:
    module = import_module(resolve_module_name(packaged))
    return _invoke_main(module, argv)
