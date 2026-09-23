#!/bin/sh
set -e

# ensure we are in the hpmor root dir
script_dir=$(dirname "$0")
cd "$script_dir/.." || exit 1

# the one-volume PDF hpmor.pdf
latexmk hpmor
