#!/bin/sh

echo === 8. HTML comparison with latest release ===

script_dir=$(dirname $0)
cd $script_dir/../..

source_file="hpmor.html"
target_file="hpmor-html-diff.log"

echo ==== 8.1 downloading from latest release ====
wget --quiet https://github.com/entorb/hpmor-de/releases/latest/download/hpmor.html -O hpmor-prev.html
# latest release https://github.com/entorb/hpmor-de/releases/latest/download/hpmor.html
# WorkInProgress https://github.com/entorb/hpmor-de/releases/download/WorkInProgress/hpmor.html

echo ==== 8.2 diff ====
diff -U 0 -s hpmor-prev.html $source_file >$target_file
