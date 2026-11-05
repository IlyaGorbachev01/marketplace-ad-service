#!/bin/bash
set -e

uv run alembic upgrade head

uv run python -m bin.outbox &
outbox_pid=$!

uv run python -m bin.api &
api_pid=$!

shutdown() {
  kill "$api_pid" "$outbox_pid" 2>/dev/null || true
  wait "$api_pid" "$outbox_pid" 2>/dev/null || true
}
trap shutdown EXIT INT TERM

wait -n "$api_pid" "$outbox_pid"
