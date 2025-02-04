#!/bin/sh

# ensure we are in the hpmor root dir
script_dir=$(cd $(dirname $0) && pwd)
cd $script_dir/..

sudo apt-get install texlive-xetex texlive-lang-greek texlive-lang-german latexmk
