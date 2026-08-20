#!/bin/sh

# ensure we are in the hpmor root dir
script_dir=$(cd $(dirname $0) && pwd)
cd "$script_dir"/..

latexmk -C
rm -rf *.pdf
rm -rf *.log
rm -rf chapters/*-autofix.tex
rm -rf chapters/*.aux
rm -rf hpmor-prev.html
rm -rf hpmor.docx
rm -rf hpmor.epub
rm -rf hpmor.fb2
rm -rf hpmor.html
rm -rf hpmor.mobi
rm -rf tmp/
