#!/bin/bash
# SessionStart hook: installs the toolchain this repo's evidence pipeline
# and test suite depend on, so both work without manual setup in a fresh
# session. Idempotent - safe to re-run; skips anything already present
# (the container's filesystem persists across session starts once this
# hook has run once, per Claude Code on the web's caching).
set -euo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

# --- Python deps: the evidence-capture pipeline + pytest suite ---
# (README.md "Running it": pip install crosshair-tool jsonschema pyyaml pytest)
pip install --quiet --disable-pip-version-check \
  crosshair-tool jsonschema pyyaml pytest

# --- .NET SDK + Dafny (Phase C) ---
# Pinned to Dafny 4.11.0, verified 2026-07-06 against this exact version:
# false-zero output format confirmed ("Dafny program verifier finished
# with N verified, 0 errors"), failure exit code confirmed as 4 (not 1),
# and the vacuous-precondition parsing risk confirmed real on this build
# (see KNOWN_LIMITATIONS.md, Phase C Gate C1). Pinning avoids silently
# picking up a different Dafny version with different output conventions
# in a future session - the same discipline this repo already applies to
# crosshair-tool 0.0.107.
#
# GitHub release downloads are blocked by this environment's egress
# policy (confirmed via the proxy status endpoint) - Dafny is installed
# entirely via apt (the .NET SDK) and NuGet (the dafny dotnet tool),
# never GitHub.
DAFNY_VERSION="4.11.0"

if ! command -v dotnet >/dev/null 2>&1 && [ ! -x /usr/lib/dotnet/dotnet ]; then
  apt-get update -qq
  apt-get install -y -qq dotnet-sdk-8.0
fi

export PATH="$PATH:/usr/lib/dotnet:/root/.dotnet/tools"
if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  echo 'export PATH="$PATH:/usr/lib/dotnet:/root/.dotnet/tools"' >> "$CLAUDE_ENV_FILE"
fi

INSTALLED_VERSION=""
if command -v dafny >/dev/null 2>&1; then
  INSTALLED_VERSION="$(dafny --version 2>&1 | head -1 | grep -oE '^[0-9]+\.[0-9]+\.[0-9]+' || true)"
fi

if [ "$INSTALLED_VERSION" != "$DAFNY_VERSION" ]; then
  if [ -n "$INSTALLED_VERSION" ]; then
    dotnet tool update --global dafny --version "$DAFNY_VERSION"
  else
    dotnet tool install --global dafny --version "$DAFNY_VERSION"
  fi
fi
