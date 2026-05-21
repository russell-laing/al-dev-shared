#!/usr/bin/env bash
# al-hook-compile.sh — AL compilation hook for al-dev-develop

set -e

if [[ ! -f "app.json" ]]; then
    exit 0
fi

# Create .dev directory if it doesn't exist
mkdir -p .dev

# Run compilation with output redirected to file only
al-compile --output .dev/compile-errors.log

# Exit with success; errors are logged to file, not stdout
exit 0
