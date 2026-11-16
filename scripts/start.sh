#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ ! -x "$ROOT/backend/.venv/bin/uvicorn" ]]; then
  echo "Backend environment is missing. Follow the backend setup in README.md first." >&2
  exit 1
fi
if [[ ! -d "$ROOT/frontend/node_modules" ]]; then
  echo "Frontend dependencies are missing. Run npm install in frontend first." >&2
  exit 1
fi
cd "$ROOT"
"$ROOT/backend/.venv/bin/uvicorn" app.main:app --app-dir "$ROOT/backend" --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
cd "$ROOT/frontend"
npm run dev -- --host 127.0.0.1 &
FRONTEND_PID=$!
cleanup(){ kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM
wait
