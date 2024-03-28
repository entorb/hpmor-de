#!/usr/bin/env python3
"""
Clean text.
"""

import glob
import os
import re
import sys

import helper
from bs4 import BeautifulSoup  # pip install beautifulsoup4

# my helper

os.chdir(os.path.dirname(sys.argv[0]))

translations = helper.translations
translators = translations.keys()

# make output dirs
for translator in translations.keys():
    os.makedirs(f"3-clean/{translator}/", exist_ok=True)


def html_modify():
    """Modify the HTML."""
    html_start = """<!DOCTYPE html>
<html lang="de">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<meta name="author" content="Eliezer Yudkowsky" />
<title>Harry Potter and the Methods of Rationality</title>
</head>
<body>
"""
    html_end = "</body></html>"
    for translator in translators:
        print("===" + translator + "===")

        for fileIn in sorted(glob.glob(f"2-extract/{translator}/*.html")):
            (filePath, fileName) = os.path.split(fileIn)
            fileOut = f"3-clean/{translator}/{fileName}"
            with open(fileIn, encoding="utf-8", newline="\n") as fh:
                cont = fh.read()
            soup = BeautifulSoup(cont, features="html.parser")

            # find header
            myElement = soup.find("h1")
            myTitle = myElement.text  # chars only, no tags
            myElement.replace_with("")
            del myElement
            print(myTitle)

            # find body text
            myElement = soup
            s = str(myElement)
            # s = myElement.prettify()

            s = html_tuning(s)
            myElement = BeautifulSoup(s, features="html.parser")
            # myBody = myElement.prettify()
            # myBody = myElement.encode()
            myBody = str(myElement)
            del myElement

            out = f"<h1>{myTitle}</h1>\n{myBody}\n"

            with open(fileOut, mode="w", encoding="utf-8", newline="\n") as fh:
                fh.write(html_start)
                fh.write(out)
                fh.write(html_end)


def html_tuning(s: str) -> str:
    """
    Cleanup spans and divs.

    fix small typos
    fix "
    TODO: add unit tests!
    """
    # end of line
    s = re.sub("\r\n", "\n", s)

    # drop empty tags 3x
    s = re.sub(r"<(\w+)>\s*</\1>", "", s, flags=re.DOTALL | re.IGNORECASE)
    s = re.sub(r"<(\w+)>\s*</\1>", "", s, flags=re.DOTALL | re.IGNORECASE)
    s = re.sub(r"<(\w+)>\s*</\1>", "", s, flags=re.DOTALL | re.IGNORECASE)

    # spans and divs
    s = cleanup_spans(s)
    s = cleanup_divs(s)

    # <BR>
    # 4x br -> 2x br
    s = re.sub(
        r"<br/>\s*<br/>\s*<br/>\s*<br/>",
        "<br/><br/>",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # 3x br -> 2x br
    s = re.sub(
        r"<br/>\s*<br/>\s*<br/>",
        "<br/><br/>",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # double br: remove spaces
    s = re.sub(r"<br/>\s+<br/>", "<br/><br/>", s, flags=re.DOTALL | re.IGNORECASE)

    # p instead of br
    # if more than 300 char -> use p instead of br
    s = re.sub("<br/>\n(.{200,})\n", r"<p>\n\1\n</p>", s, flags=re.IGNORECASE)
    s = re.sub(r"<br/>\s*<p>", "<p>", s, flags=re.DOTALL | re.IGNORECASE)
    s = re.sub(r"</p>\s*<br/>", "</p>", s, flags=re.DOTALL | re.IGNORECASE)

    # char tunings
    # ... -> …
    s = s.replace("...", "…")

    # remove space before puctuation
    # s = re.sub(" ([\.,:;](?=\.))", r"\1 ", s)
    # add space after puctuation
    # s = re.sub("([a-zA-Z][\.,:;])([a-zA-Z])", r"\1 \2", s)

    # spaces before " at lineend
    s = re.sub('\\s+"\n', '"\n', s, flags=re.DOTALL | re.IGNORECASE)
    # remove linebreaks from sentences containing quotation marks
    # 3x
    s = re.sub(
        r'("\w[^"]+)\s+<br/>\s+([^"]+)\s+<br/>\s+([^"]+)\s+<br/>\s+([^"]+")',
        r"\1 \2 \3 \4",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # 2x
    s = re.sub(
        r'("\w[^"]+)\s+<br/>\s+([^"]+)\s+<br/>\s+([^"]+")',
        r"\1 \2 \3",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # 1x
    s = re.sub(
        r'("\w[^"]+)\s+<br/>\s+([^"]+")',
        r"\1 \2",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # br -> p
    s = "<p>" + s + "</p>"
    s = re.sub("<br/><br/>", "</p><p>", s, flags=re.DOTALL | re.IGNORECASE)

    # some known text errors
    s = s.replace('."Wie kannst du das', '. "Wie kannst du das')
    s = s.replace('Mannes erstickte."Peter hatte', 'Mannes erstickte. "Peter hatte')
    s = s.replace(
        'begann zu gehen."Und pass auf, dass',
        'begann zu gehen. "Und pass auf, dass',
    )
    s = s.replace('Auroren,"ist der Grund', 'Auroren, "ist der Grund')
    s = s.replace('Draco?"sagte', 'Draco?" sagte')
    s = s.replace('Blick zu."Hör mal', 'Blick zu. "Hör mal')
    s = s.replace('Kopf."Ich', 'Kopf. "Ich')
    s = s.replace('Bäume."Halte', 'Bäume. "Halte')
    s = s.replace('Quirrell."Ich denke', 'Quirrell. "Ich denke')
    s = s.replace('Verteidigungsprofessor."Wir', 'Verteidigungsprofessor. "Wir')
    s = s.replace('Glück."Also', 'Glück. "Also')

    # # Quotations
    # # nice looking quotation signs
    # # en &ldquo;example&rdquo;
    # # de &bdquo;Beispiel&ldquo;
    # q_left = "&bdquo;"
    # q_right = "&ldquo;"

    # # left
    # s = re.sub('([\s\(]+)"', rf"\1{q_left}", s)
    # s = re.sub('(\.\.\.)"(\w)', rf"\1{q_left}\2", s)
    # # right
    # s = re.sub('"([\s,\.!\?\)\-]+)', rf"{q_right}\1", s)
    # s = re.sub('([\w])"([;])', rf"\1{q_right}\2", s)

    # whitespace at start of line
    s = re.sub("\n\\s+", "\n", s)
    # multiple spaces
    s = re.sub("  +", " ", s)
    # empty lines
    s = re.sub("\n\\s*\n+[\\s\n]*", "\n", s)

    return s


def cleanup_spans(s: str) -> str:
    """
    Clean the span tags.
    """
    # harmonize
    s = s.replace(
        '<span style="text-decoration:underline;">',
        '<span class="user_underlined">',
    )

    # empty spans 3x
    s = re.sub(
        r'<span class="[^"]+">\s*</span>',
        "",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    s = re.sub(
        r'<span class="[^"]+">\s*</span>',
        "",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    s = re.sub(
        r'<span class="[^"]+">\s*</span>',
        "",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    assert "€" not in s, "ERROR: could not mask closing </span> by €"
    # mask closing spans for next re
    s = re.sub(
        "</span>",
        "€",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    #  user_italic + user_italic
    s = re.sub(
        r'<span class="user_italic">(\s*)<span class="user_italic">([^€]*)€(\s*)€',
        r"<em>\1\2\3</em>",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    #  user_italic + user_normal
    s = re.sub(
        r'<span class="user_italic">(\s*)<span class="user_normal">([^€]*)€(\s*)€',
        r"\1\2\3",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    s = re.sub(
        '<span class="user_underlined">([^€]*)€',
        r"<u>\1</u>",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    s = re.sub(
        '<span class="user_italic">([^€]*)€',
        r"<em>\1</em>",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    s = re.sub(
        '<span class="user_bold">([^€]*)€',
        r"<b>\1</b>",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    # again replace by b and em
    s = re.sub(
        '<span class="user_italic">([^€]*)€',
        r"<em>\1</em>",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    s = re.sub(
        '<span class="user_bold">([^€]*)€',
        r"<b>\1</b>",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    s = re.sub(
        '<span class="user_italic">([^€]*)€',
        r"<em>\1</em>",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    s = re.sub(
        '<span class="user_bold">([^€]*)€',
        r"<b>\1</b>",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # drop user_normal 2x
    s = re.sub(
        '<span class="user_normal">([^€]*)€',
        r"\1",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    s = re.sub(
        '<span class="user_normal">([^€]*)€',
        r"\1",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )

    if "<span" in s:
        with open("0error.html", mode="w", encoding="utf-8", newline="\n") as fh:
            fh.write(s)
        assert "<span" not in s, "ERROR: span still in"

    return s


def cleanup_divs(s: str) -> str:
    """
    Clean the DIV tags.
    """
    if "€" in s:
        with open("0error.html", mode="w", encoding="utf-8", newline="\n") as fh:
            fh.write(s)
        assert "€" not in s, "ERROR: could not mask closing </div> by €"

    # mask closing div for next re
    s = s.replace("</div>", "€")

    s = re.sub(
        '<div class="user_center">([^€]*)€',
        r"<center>\1</center>",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    s = re.sub(
        '<div class="user_right">([^€]*)€',
        r"<right>\1</right>",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    s = re.sub(
        '<div class="user_left">([^€]*)€',
        r"<left>\1</left>",
        s,
        flags=re.DOTALL | re.IGNORECASE,
    )
    assert "<div" not in s, "ERROR: div still in"
    return s


if __name__ == "__main__":
    html_modify()
