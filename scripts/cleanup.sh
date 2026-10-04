#!/bin/sh
set -e
cd "$(dirname "$0")/.."

latexmk -C
rm -rf ./*.log
rm -rf ./*.pdf
rm -rf chapters/*-autofix.tex
rm -rf chapters/*.aux
rm -rf hpmor-prev.html
rm -rf hpmor.docx
rm -rf hpmor.epub
rm -rf hpmor.fb2
rm -rf hpmor.html
rm -rf hpmor.mobi
rm -rf tmp/
