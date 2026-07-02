# Companion Packages

This directory contains harness-specific installable packages that complement the
shared authored surface in `profile-al-dev-shared/`.

## Rules

- Each installable package lives at `companions/<harness>/<package>/`
- Package-local runtime behavior stays inside the package root
- Shared behavior belongs in `profile-al-dev-shared/`
- Vault and other non-AL/BC packages are out of scope for this migration wave
