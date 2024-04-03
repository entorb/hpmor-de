#!/bin/sh

# ensure we are in the hpmor root dir
script_dir=$(dirname $0)
cd $script_dir/..

# first full pdf
latexmk hpmor
# second parallel building for 6 volumes
latexmk hpmor-1 &
latexmk hpmor-2 &
latexmk hpmor-3 &
latexmk hpmor-4 &
latexmk hpmor-5 &
latexmk hpmor-6 &

# # make all
# latexmk
