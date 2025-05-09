#!/usr/bin/env python3
# by Torben Menke https://entorb.net

"""
Modify flattened .tex file.
"""

import datetime as dt
import os
import re
from pathlib import Path

os.chdir(Path(__file__).parent.parent.parent)

source_file = Path("tmp/hpmor-epub-2-flatten.tex")
target_file = Path("tmp/hpmor-epub-3-flatten-mod.tex")

if __name__ == "__main__":
    print("=== 3. modify flattened file ===")

    with source_file.open(encoding="utf-8", newline="\n") as fh_in:
        cont = fh_in.read()

    # \today
    date_str = dt.datetime.now(dt.UTC).date().strftime("%d.%m.%Y")
    cont = cont.replace("\\today{}", date_str)

    # empty the newenvironments: headlines, writtenNote, playdialog
    #  to prevent implications on other cleanup scripts
    cont = re.sub(
        r"\\newenvironment\{(headlines|writtenNote|playdialog)\}.*?\n\n",
        r"\\newenvironment{\1}{}{}\n\n",
        cont,
        flags=re.DOTALL,
        count=3,
    )

    # writtenNote env -> \writtenNoteA
    cont = re.sub(
        r"\s*\\begin\{writtenNote\}\s*(.*?)\s*\\end\{writtenNote\}",
        r"\\writtenNoteA{\1}",
        cont,
        flags=re.DOTALL,
    )

    # fix chapterOpeningAuthorNote
    # not used in DE version

    # some cleanup
    cont = cont.replace("\\hplettrineextrapara\n", "")

    # additional linebreaks in verses of chapter 64
    cont = cont.replace("\\\\\n\n", "\n\n")

    # manual pagebreaks
    cont = re.sub(r"\\clearpage(\{\}|)\n?", "", cont)

    # \vskip 1\baselineskip plus .5\textheight minus 1\baselineskip
    cont = re.sub(r"\\vskip .*\\baselineskip", "", cont)

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
    cont = re.sub(r"\\censor\{[^}]*\}", r"xxxxxx", cont)

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
        r"\\includegraphics\[[^\]]*\]\{[^\}]*\}",
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

    with target_file.open(mode="w", encoding="utf-8", newline="\n") as fh_out:
        fh_out.write(cont)
