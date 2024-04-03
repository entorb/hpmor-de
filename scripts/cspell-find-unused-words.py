#!/usr/bin/env python3
# by Torben Menke https://entorb.net

"""
Remove unused words from cspell wordlist.

reads wordlist
reads chapter LaTeX files, removes comments
"""

import re
from pathlib import Path

path_to_wordlist = Path("cspell-words.txt")
words = path_to_wordlist.read_text(encoding="utf-8").splitlines()

# remove duplicates in source file
words = set(words)
words = sorted(words, key=lambda x: x.lower())
# path_to_wordlist.write_text("\n".join(words))

cont_all_chapter: str = ""
for chapter_file in sorted(Path("chapters").glob("*.tex")):
    cont_all_chapter += chapter_file.read_text(encoding="utf-8")

# remove comments
cont_all_chapter = re.sub(r"(?<!\\)%.*\n", r"", cont_all_chapter)

# p = Path("join.tex")
# p.write_text(cont_all_chapter)

words_in_doc: list[str] = []

for word in words:
    if word not in cont_all_chapter:
        print(word)
    else:
        words_in_doc.append(word)
    # words used only once might contain typos
    # cnt = cont_all_chapter.count(word)
    # if cont_all_chapter.count(word) == 1:
    #     print(word)

words_in_doc = sorted(words_in_doc, key=lambda x: x.lower())


# path_to_wordlist_clean = Path("cspell-words-clean.txt")
# path_to_wordlist_clean.write_text("\n".join(words_in_doc))
# path_to_wordlist.write_text("\n".join(words_in_doc))
