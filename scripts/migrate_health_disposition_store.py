#!/usr/bin/env python3
"""Compatibility wrapper for the packaged health disposition migration CLI."""

try:
    from scripts.al_dev_tools.health.migrate_health_disposition_store import *  # noqa: F401,F403
    from scripts.al_dev_tools.health.migrate_health_disposition_store import main
except ModuleNotFoundError:
    from al_dev_tools.health.migrate_health_disposition_store import *  # noqa: F401,F403
    from al_dev_tools.health.migrate_health_disposition_store import main


if __name__ == "__main__":
    main()
