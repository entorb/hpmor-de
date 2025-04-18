#!/usr/bin/env python3
# by Torben Menke https://entorb.net
# ruff: noqa: RUF001

"""
HTML modifications.
"""

import re
import sys
from pathlib import Path

from lxml import etree  # pip install lxml

sys.path.append(str(Path(__file__).resolve().parent.parent))
from check_chapters_settings import settings

LANG = settings["lang"]

source_file = Path("tmp/hpmor-epub-5-html-unmod.html")
target_file = Path("hpmor.html")


def check_html(cont: str) -> None:
    """Check html syntax."""
    parser = etree.XMLParser(recover=False)  # Do not auto-fix errors
    try:
        etree.fromstring(cont, parser)
    except etree.XMLSyntaxError as e:
        print("HTML Error:", e)
        sys.exit(1)
        # raise


def fix_ellipsis(s: str) -> str:
    """
    Fix ellipsis spacing for ebooks.
    """
    if LANG == "DE":
        # this was redundant to the new DE rules in check_chapters.py
        # before opening DE-quotes: add space
        # s = re.sub(r"…(?=[„])", "… ", s)
        return s
    # 1. remove all spaces around ellipsis
    s = re.sub(r" *… *", "…", s)
    # 2. recreate some spaces
    # before punctuation : no space, so covered by 1.
    # between words
    s = re.sub(r"(?<=[\w])…(?=[\w])", "… ", s)
    # after punctuation: add space
    s = re.sub(r"(?<=[\.\?!:,;])…", r" …", s)
    # fine-tuning </em>… and …<em>
    s = re.sub(r"(?<=</em>)…", "… ", s)
    s = re.sub(r"…(?=<em>)", "… ", s)
    # before opening EN-quotes: add space
    # s = re.sub(r"…(?=[“])", "… ", s)
    # NO: before opening DE-quotes: add space
    # s = re.sub(r"…(?=[„])", "… ", s)
    return s


if __name__ == "__main__":
    print("=== 6. HTML modifications ===")

    with source_file.open(encoding="utf-8", newline="\n") as fh_in:
        cont = fh_in.read()
    print("checking source html")
    check_html(cont)

    # remove strange leftovers from tex -> html conversion
    cont = re.sub(
        r"(</header>).*?(<p>Fanfiction von)",
        r"\1\n\2",
        cont,
        flags=re.DOTALL | re.IGNORECASE,
        count=1,
    )

    # stray </div> leftover
    cont = re.sub(
        r"(github.com/rrthomas/hpmor/</a></span><br />\s+</p>)\s+</div>",
        r"\1",
        cont,
        flags=re.DOTALL | re.IGNORECASE,
        count=1,
    )

    # remove duplication of author name
    cont = re.sub(
        r"""<p>Fanfiction.*?<p>Basierend auf der Harry Potter Reihe von J. K. Rowling.*?</p>""",  # noqa: E501
        "<p>Fanfiction basierend auf der Harry Potter Reihe von J. K. Rowling</p>",
        cont,
        flags=re.DOTALL | re.IGNORECASE,
        count=1,
    )

    # now done via pandoc -V lang=de in step_5.sh
    # # set language
    # cont = re.sub(
    #     r'(<html [^>]*) lang="" xml:lang=""',
    #     r'\1 lang="de" xml:lang="de"',
    #     cont,
    #     count=1,
    # )

    # fix spaces around ellipsis
    cont = fix_ellipsis(cont)

    # doc structure (not needed any more, using calibi --level1-toc flag instead)
    # sed -i 's/<h1 /<h1 class="part"/g' $target_file
    # sed -i 's/<h2 /<h2 class="chapter"/g' $target_file
    # sed -i 's/<h3 /<h3 class="section"/g' $target_file

    # remove ids from chapters since umlaute cause problem
    cont = re.sub(
        r'(<h\d)\s+id="[^"]+"',
        r"\1",
        cont,
        flags=re.DOTALL | re.IGNORECASE,
    )
    cont = re.sub(
        r'(<h\d\s+class="unnumbered")\s+id="[^"]+"',
        r"\1",
        cont,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # add part numbers
    part_no = 0
    while "<h1>" in cont:
        part_no += 1
        cont = cont.replace("<h1>", f"<h1_DONE>{part_no}. ", 1)
    cont = cont.replace("<h1_DONE>", "<h1>")

    # add chapter numbers
    chapter_no = 0
    while "<h2>" in cont:
        chapter_no += 1
        cont = cont.replace("<h2>", f"<h2_DONE>{chapter_no}. ", 1)
    cont = cont.replace("<h2_DONE>", "<h2>")

    # fix double rules
    # cont = cont.replace("<hr />\n<hr />", "<hr />")
    cont = re.sub(
        r"<hr */>\n<hr */>",
        r"<hr />",
        cont,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # fixing linebreak at author's comment
    cont = cont.replace("<p>E. Y.: </p>\n<p>", "<p>E.Y.: ")

    # converting "color-marked" styles of 1.sh back to proper style classes
    cont = re.sub(
        r'<(div|span) style="color: (parsel|writtenNote|McGonagallWhiteBoard|headline)"',  # noqa: E501
        r'<\1 class="\2"',
        cont,
    )

    # add css style file format for \emph in \emph
    with Path("scripts/ebook/html.css").open(encoding="utf-8", newline="\n") as fh_in:
        css = fh_in.read()
    cont = cont.replace("</style>\n", css + "\n</style>\n")

    print("checking target html")
    check_html(cont)

    # remove training slashes to satisfy https://validator.w3.org
    cont = cont.replace("<br />", "<br>")
    cont = cont.replace("<hr />", "<hr>")
    cont = re.sub(
        r"(<meta [^>]*) />",
        r"\1>",
        cont,
    )

    with target_file.open(mode="w", encoding="utf-8", newline="\n") as fh_out:
        fh_out.write(cont)
