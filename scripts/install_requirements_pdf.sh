#!/bin/sh
set -e
cd "$(dirname "$0")/.."

sudo apt-get install -y texlive-xetex texlive-lang-greek texlive-lang-german latexmk
