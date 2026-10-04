#!/bin/sh
set -e
cd "$(dirname "$0")/.."

sudo apt-get install -y texlive-extra-utils pandoc calibre imagemagick ghostscript
# pandoc calibre : for ebook converting
# texlive-extra-utils : for latexpand
# imagemagick ghostscript : for pdf title page to image conversion

pip install -r python-requirements.txt
