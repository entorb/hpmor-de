#!/usr/bin/env python3
# by Torben Menke https://entorb.net
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
cont = cont.replace("\\hplettrineextrapara", "")

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


# for spellcheck doc version -> not working, make_ebook-sh runs forever...
# cont = re.sub(r"\\spell\{.*?\}+", "spell", cont)

with open(target_file, mode="w", encoding="utf-8", newline="\n") as fhOut:
    fhOut.write(cont)
