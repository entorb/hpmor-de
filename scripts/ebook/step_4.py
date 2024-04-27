#!/usr/bin/env python3
# by Torben Menke https://entorb.net

"""
Parselify flattened .tex file.
"""

import os
import re
from pathlib import Path

os.chdir(Path(__file__).parent.parent.parent)

source_file = Path("tmp/hpmor-epub-3-flatten-mod.tex")
target_file = Path("tmp/hpmor-epub-4-flatten-parsel.tex")


def convert_parsel(s: str) -> str:
    """Convert text to Parsel."""
    # TODO: for spellcheck doc version we should return here
    # return s
    # small ss -> ß -> sss ; s->ss
    s = s.replace("ss", "ß").replace("s", "ss").replace("ß", "sss")
    # capital S -> Ss ; capital SS -> SSS ; S->SS
    s = s.replace("SS", "ẞ").replace("S", "Ss").replace("ẞ", "SSS")
    # small zz -> zzz ; z->zz
    s = s.replace("zz", "ß").replace("z", "zz").replace("ß", "zzz")
    # capital Z -> Zz ; ZZ->ZZZ
    s = s.replace("ZZ", "ẞ").replace("Z", "Zz").replace("ß", "ZZZ")
    # small x -> xs
    s = s.replace("x", "xs")
    return s


if __name__ == "__main__":
    print("=== 4. parselify flattened file in python ===")

    with source_file.open(encoding="utf-8", newline="\n") as fh_in:
        cont = fh_in.read()

    # \parsel
    my_matches = re.finditer(r"(\\parsel\{([^\}\\]+)\})", cont)
    for my_match in my_matches:
        was = my_match.group(1)
        womit = convert_parsel(my_match.group(2))
        cont = cont.replace(was, "\\parsel{" + womit + "}")

    with target_file.open(mode="w", encoding="utf-8", newline="\n") as fh_out:
        fh_out.write(cont)
