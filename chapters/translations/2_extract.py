#!/usr/bin/env python3

# TODO: fix ruff findings
# ruff: noqa

"""
Extract text from downloaded HTML files.
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
    os.makedirs(f"2-extract/{translator}/", exist_ok=True)


def extract_chapter_text():
    """
    Extract chapter text from html and writes result into 2-extracted/ .

    2 modifications are done: removal of comments and removal of javascript
    """
    for translator in translators:
        print("===" + translator + "===")
        for fileIn in sorted(glob.glob(f"1-download/{translator}/*.html")):
            (filePath, fileName) = os.path.split(fileIn)
            fileOut = f"2-extract/{translator}/{fileName}"
            with open(fileIn, encoding="utf-8", newline="\n") as fh:
                cont = fh.read()

            # cleanup comments and scripts
            cont = re.sub("<!--.*?-->", "", cont, flags=re.DOTALL)
            cont = re.sub(
                "<script.*?</script>",
                "",
                cont,
                flags=re.DOTALL | re.IGNORECASE,
            )

            soup = BeautifulSoup(cont, features="html.parser")

            myTitle = ""
            myBody = ""

            # find chapter name from dropdown
            myElement = soup.find("select", {"id": "kA"})
            myElement = myElement.find("option", {"selected": "selected"})
            myTitle = myElement.text  # chars only, no tags

            # find body text
            myElement = soup.find("div", {"class": "user-formatted-inner"})
            # myBody = myElement.prettify()
            # myBody = myElement.encode()
            myBody = str(myElement)
            del myElement

            # remove linebreaks and multiple spaces
            myTitle = re.sub(r"\s+", " ", myTitle, flags=re.DOTALL | re.IGNORECASE)
            print(myTitle)
            # remove outer encapsolating div start and end
            myBody = re.sub("^<div[^>]*>", "", myBody, flags=re.DOTALL | re.IGNORECASE)
            myBody = re.sub("</div>[^>]*$", "", myBody, flags=re.DOTALL | re.IGNORECASE)

            out = f"<h1>{myTitle}</h1>\n{myBody}\n"

            with open(fileOut, mode="w", encoding="utf-8", newline="\n") as fh:
                fh.write(out)


if __name__ == "__main__":
    extract_chapter_text()
