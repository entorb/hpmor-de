#!/bin/sh

# based on work by yeKcim
# https://github.com/yeKcim/hpmor/tree/master/ebook

echo === 1. prepare .tex file, based on hpmor.tex===

# ensure we are in the hpmor root dir
script_dir=$(cd `dirname $0` && pwd)
cd $script_dir/..

source_file="hpmor.tex"
# source_file="layout/test.tex"
target_file="hpmor-epub-1.tex"
cp $source_file $target_file

# insert packages to load
# sed '3i\\\input{layout/hp-format}\n\\input{layout/hp-markup}\n\\usepackage{polyglossia}\n\\setmainlanguage{german}\n\\setdefaultlanguage[spelling = new]{german}' $source_file > $target_file
sed -i '3i\\\usepackage{polyglossia}\n\\setdefaultlanguage[variant = german, spelling = new, babelshorthands = true, script = latin]{german}\n\\enablehyphenation' $target_file
sed -i '8i\\\input{layout/hp-format}\n\\input{layout/hp-markup}' $target_file

# remove loading of hp-contents file
sed -i '/\\\input{layout\/hp-contents}/d' $target_file

# overwrite the headlines env, since it makes problems in pandoc
sed -i '10i\\\renewenvironment{headlines}{}{}' $target_file
# overwrite the writtenNote env, since it makes problems in pandoc
sed -i '11i\\\renewenvironment{writtenNote}{}{}' $target_file

# use \writtenNoteA instead of writtenNote env
sed -i '12i\\\newcommand\{\\writtenNoteA}[1]{\\par\\textcolor{writtenNote}{#1}}' $target_file

# hack: using a color to convert the custom commands to css styles
sed -i '13i\\\renewcommand\{\\parsel}[1]{\\textcolor{parsel}{#1}}' $target_file
sed -i '13i\\\renewcommand\{\\McGonagallWhiteBoard}[1]{\\begin{center}\\textcolor{McGonagallWhiteBoard}{#1}\\end{center}}' $target_file
sed -i '13i\\\renewcommand\{\\headline}[1]{\\begin{center}\\textcolor{headline}{#1}\\end{center}}' $target_file
sed -i '13i\\\renewcommand\{\\inlineheadline}[1]{\\textcolor{headline}{#1}}' $target_file


