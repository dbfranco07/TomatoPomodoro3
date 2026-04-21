#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "=== Backend tests (pytest) ==="
source "$ROOT/.venv/bin/activate"
pytest "$ROOT/tests" -v

echo ""
echo "=== Frontend tests (vitest) ==="
cd "$ROOT/tests/js"
npm install --silent
npx vitest run

echo ""
echo "All tests passed."
