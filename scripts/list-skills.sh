#!/usr/bin/env bash
set -euo pipefail

# From mattpocock/skills; see README.md and LICENSE at the repository root.

REPO="$(cd "$(dirname "$0")/.." && pwd)"

cd "$REPO"
find . -name SKILL.md -not -path '*/node_modules/*' | sed 's|^\./||' | sort
