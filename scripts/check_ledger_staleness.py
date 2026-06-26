#!/usr/bin/env python3
"""Compatibility wrapper for the packaged ledger staleness checker."""

try:
    from scripts.al_dev_tools.health.check_ledger_staleness import *  # noqa: F401,F403
    from scripts.al_dev_tools.health.check_ledger_staleness import main
except ModuleNotFoundError:
    from al_dev_tools.health.check_ledger_staleness import *  # noqa: F401,F403
    from al_dev_tools.health.check_ledger_staleness import main


if __name__ == "__main__":
    raise SystemExit(main())
