#!/bin/sh

# ensure we are in the hpmor root dir
script_dir=$(cd $(dirname $0) && pwd)
cd $script_dir/..

sudo apt-get install texlive-extra-utils pandoc calibre imagemagick ghostscript
# pandoc calibre : for ebook converting
# texlive-extra-utils : for latexpand
# imagemagick ghostscript : for pdf title page to image conversion

pip install -r python-requirements.txt
