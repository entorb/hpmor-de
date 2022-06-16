#!/bin/sh

# ensure we are in the hpmor root dir
script_dir=$(cd `dirname $0` && pwd)
cd $script_dir/..

# TODO:
# image on last page

sh ebook/0.sh
sh ebook/1.sh
sh ebook/2.sh
# sh ebook/3.sh
python3 ebook/3.py
python3 ebook/4.py
sh ebook/5.sh
# sh ebook/6.sh
python3 ebook/6.py
sh ebook/7.sh

# rm -rf hpmor-epub*.tex
# rm -rf hpmor-epub*.html
# rm -rf ebook/tmp/title.png




# # TODO
# # cd ebook
# # ./1_latex2html.py && ./2_html2epub.sh

# rm -f hpmor_epub.tex hpmor_flatten.tex
