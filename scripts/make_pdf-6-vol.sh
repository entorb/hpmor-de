#!/bin/sh
set -e
cd "$(dirname "$0")/.."

# the six individual volumes hpmor-1.pdf .. hpmor-6.pdf
#
# One latexmk call, so the volumes are typeset one after another. Do NOT run
# them in parallel here: they all \include the same chapter files and write
# the same chapters/*.aux, so concurrent runs silently corrupt each other's
# cross-references and page numbers.
latexmk hpmor-1 hpmor-2 hpmor-3 hpmor-4 hpmor-5 hpmor-6
