#!/usr/bin/env python3

# TODO: fix ruff findings
# ruff: noqa

"""
Convert HTML to LaTeX.
"""

import glob
import os
import subprocess
import sys

import helper

# my helper

os.chdir(os.path.dirname(sys.argv[0]))

translations = helper.translations
translators = translations.keys()

# make output dirs
for translator in translations.keys():
    os.makedirs(f"4-latex/{translator}/", exist_ok=True)


def html2latex():
    """
    Convert LaTeX code to HTML.
    """
    for translator in translators:
        print("===" + translator + "===")
        for fileIn in sorted(glob.glob(f"3-clean/{translator}/*.html")):
            print(fileIn)
            fileOut = fileIn.replace("3-clean/", "4-latex/").replace(".html", ".tex")
            # pandoc -s fileIn -o fileOut
            process = subprocess.run(
                ["pandoc", "-s", fileIn, "-o", fileOut],
                capture_output=True,
                text=True,
                check=False,
            )
            print(process.stdout)


if __name__ == "__main__":
    html2latex()
