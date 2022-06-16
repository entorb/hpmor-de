#!/bin/sh

# ensure we are in the hpmor root dir
script_dir=$(cd `dirname $0` && pwd)
cd $script_dir/..

latexmk -C
rm -rf chapters/*.aux
rm -rf chapters/*-autofix.tex
rm -rf ebook/tmp
