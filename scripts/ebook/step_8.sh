#!/bin/sh
set -e

echo "=== 8. HTML comparison with release WorkInProgress ==="

# ensure we are in the hpmor root dir
script_dir=$(dirname "$0")
cd "$script_dir/../.." || exit 1

source_file="hpmor.html"
target_file="hpmor-html-diff.log"
# addressed by tag, so this keeps working whatever /releases/latest/
# happens to point at
url="https://github.com/entorb/hpmor-de/releases/download/WorkInProgress/hpmor.html"

echo "==== 8.1 downloading from release WorkInProgress ===="
if ! wget --quiet "$url" -O hpmor-prev.html; then
  echo "ERROR: could not download $url" >&2
  rm -f hpmor-prev.html
  exit 1
fi

echo "==== 8.2 diff ===="
# diff exits 1 when the files differ, which is the expected case here
diff -U 0 -s hpmor-prev.html "$source_file" >"$target_file" || true
