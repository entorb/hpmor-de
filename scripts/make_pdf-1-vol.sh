#!/bin/sh
set -e
cd "$(dirname "$0")/.."

# the one-volume PDF hpmor.pdf
latexmk hpmor
