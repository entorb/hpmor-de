#!/bin/sh
set -e
cd "$(dirname "$0")/.."

out=$(mktemp)
trap 'rm -f "$out"' EXIT INT TERM

status=0
prek run --all-files >"$out" 2>&1 || status=$?

if [ $status -ne 0 ]; then
  head -n 100 "$out"
fi
exit $status
