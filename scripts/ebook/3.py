#!/usr/bin/env python3
# by Torben Menke https://entorb.net

# TODO: fix ruff findings
# ruff: noqa

"""
Modify flattened .tex file.
"""

import datetime as dt
import os
import re
import sys

os.chdir(os.path.dirname(sys.argv[0]) + "/../..")

source_file = "tmp/hpmor-epub-2-flatten.tex"
target_file = "tmp/hpmor-epub-3-flatten-mod.tex"

print("=== 3. modify flattened file ===")


with open(source_file, encoding="utf-8", newline="\n") as fhIn:
    cont = fhIn.read()

# \today
date_str = dt.date.today().strftime("%d.%m.%Y")
cont = cont.replace("\\today{}", date_str)

# writtenNote env -> \writtenNoteA
cont = re.sub(
    r"\s*\\begin\{writtenNote\}\s*(.*?)\s*\\end\{writtenNote\}",
    r"\\writtenNoteA{\1}",
    cont,
    flags=re.DOTALL,
)

# some cleanup
# TODO: removed when switching to Ubuntu >= 23.04,
#   since it let to a problem
#  in line 31 of tmp/hpmor-epub-3-flatten-mod.tex
# cont = cont.replace("\\hplettrineextrapara", "")

# additional linebreaks in verses of chapter 64
cont = cont.replace("\\\\\n\n", "\n\n")

# manual pagebreaks
cont = re.sub(r"\\clearpage(\{\}|)\n?", "", cont)

# \vskip 1\baselineskip plus .5\textheight minus 1\baselineskip
cont = re.sub(r"\\vskip .*?\\baselineskip", "", cont)

# remove \settowidth{\versewidth}... \begin{verse}[\versewidth]
cont = re.sub(
    r"\n[^\n]*?\\settowidth\{\\versewidth\}[^\n]*?\n(\\begin\{verse\}\[\\versewidth\])",
    r"\n\\begin{verse}",
    cont,
)

# remove \settowidth
cont = re.sub(
    r"\\settowidth\{[^\}]*\}\{([^\}]*)\}",
    r"\1",
    cont,
    flags=re.DOTALL,
)

# fix „ at start of chapter
# \lettrine[ante=„] -> „\lettrine
# \lettrinepara[ante=„] -> „\lettrine
cont = re.sub(
    r"\\(lettrine|lettrinepara)\[ante=(.)\]",
    r"\2\\lettrine",
    cont,
)

# OMakeIV sections
# not used in DE version

# \censor
cont = re.sub(r"\\censor\{.*?\}", r"xxxxxx", cont)


# # remove Deathly_Hallows_Sign.pdf and other pdf images
# # \includegraphics[scale=0.125]{images/Deathly_Hallows_Sign.pdf}
# cont = re.sub(
#     # r"\\includegraphics.*?\{images/Deathly_Hallows_Sign.*?\}",
#     r"\\includegraphics.*?\.pdf\}",
#     "",
#     cont,
# )

# remove all images
cont = re.sub(
    r"\\includegraphics\[.*?\]\{.*?\}",
    "",
    cont,
    flags=re.DOTALL,
)

# remove empty envs
cont = re.sub(
    r"\\begin\{([^\}]*)\}\s*\\end\{\1}",
    "",
    cont,
    flags=re.DOTALL,
)

# remove end stuff
cont = re.sub(
    r"(.*)\\end\{chapterOpeningAuthorNote\}.*?\\end\{document\}",
    r"\1\\end{chapterOpeningAuthorNote}\n\\end{document}",
    cont,
    flags=re.DOTALL,
    count=1,
)

with open(target_file, mode="w", encoding="utf-8", newline="\n") as fhOut:
    fhOut.write(cont)
