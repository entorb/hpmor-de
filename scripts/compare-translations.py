#!/usr/bin/env python3

# by Torben Menke https://entorb.net

# downloads other translation chapter files
# chapter-wise comparison of my version to other language
#   by counting the use of LaTeX commands like \parsel etc.s

import os
import re
import requests
import sys

list_of_latex_commands_to_search_for = [
    "\\chapter",
    "\\partchapter",
    "\\section",
    "\\latersection",
    "\\later",
    "\\shout",
    "\\scream",
    "\\prophesy",
    "\\parsel",
    "\\headline",
    "\\inlineheadline",
    "\\SPHEW",
    "\\spell",
    "\\begin{writtenNote}",
    "\\begin{em}",
    "\\emph",
    "—",
    "…",
]

# set repo language to compare with
other_lang = "en"

# ensure we are in chapter dir
dir_root = os.path.dirname(sys.argv[0]) + "/.."
os.chdir(dir_root + "/chapters")

translations = {
    "en": {
        "repo": "rrthomas/hpmor/",
    },
    "fr": {
        "repo": "yeKcim/hpmor/",
    },
    "de": {
        "repo": "entorb/hpmor-de/",
    },
}


def download_file(url: str, filepath: str):
    """download file from url to filepath"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0 ",
    }
    cont = requests.get(url, headers=headers, verify=True).content
    # verify=False -> skip SSL cert verification: CERTIFICATE_VERIFY_FAILED
    with open(filepath, mode="bw") as fh:
        fh.write(cont)


def download_all_chapters():
    baseurl = "https://raw.githubusercontent.com/<<repo>>/master/chapters/hpmor-chapter-<<chapter-no>>.tex"

    # for lang in translations.keys():
    lang = other_lang
    print(f"===downloading translation : {lang}===")
    dirout = f"translation-{lang}/"
    os.makedirs(dirout, exist_ok=True)

    repo = translations[lang]["repo"]
    for i in range(0, 122 + 1):
        ch_no = "%03d" % i
        url = baseurl.replace("<<repo>>", repo).replace("<<chapter-no>>", ch_no)
        filepath = f"{dirout}/hpmor-chapter-{ch_no}.tex"
        if not os.path.exists(filepath):
            print(filepath)
            download_file(url=url, filepath=filepath)


def get_list_of_my_chapter_files() -> list:
    """
    reads hpmor.tex, extract list of (not-commented out) chapter files
    returns list of filesnames
    """
    list_of_chapter_files = []
    with open("../hpmor.tex", mode="r", encoding="utf-8") as fh:
        lines = fh.readlines()
    lines = [elem for elem in lines if elem.startswith("\include{chapters/")]
    for line in lines:
        fileName = re.search("^.*include\{chapters/(.+?)\}.*$", line).group(1)
        list_of_chapter_files.append(fileName + ".tex")
    return list_of_chapter_files


def remove_comments(cont: str) -> str:
    """
    removes Latex comments from file contents
    """
    # fix end of line
    cont = re.sub(r"\r\n?", r"\n", cont)
    l_cont = cont.split("\n")
    l_cont_clean = []
    # remove comments
    for line in l_cont:
        if re.match("^\s*%", line):
            continue
        line = re.sub(r"(?<!\\)%.+", "", line)
        l_cont_clean.append(line)
    cont_clean = "\n".join(l_cont_clean)
    return cont_clean


def count_latex_commands(cont: str) -> dict:
    res = {}
    for command in list_of_latex_commands_to_search_for:
        c = cont.count(command)
        # print(f"{command} \t {c}")
        res[command] = c
    return res


def compare_to_lang(myFiles: list, lang="en"):
    for myFile in myFiles:
        ch_no = myFile[14:17]
        # in DE I added a prefix to the files, so this would not work for lang == "de"
        otherFile = f"translation-{lang}/hpmor-chapter-{ch_no}.tex"

        with open(myFile, mode="r", encoding="utf-8") as fh:
            cont = fh.read()
        cont = remove_comments(cont)
        res_myFile = count_latex_commands(cont)

        with open(otherFile, mode="r", encoding="utf-8") as fh:
            cont = fh.read()
        cont = remove_comments(cont)
        res_otherFile = count_latex_commands(cont)

        has_finding = False
        for command in list_of_latex_commands_to_search_for:
            c_myFile = res_myFile[command]
            c_otherFile = res_otherFile[command]
            if c_myFile != c_otherFile:
                if has_finding == False:
                    has_finding = True
                    print(myFile)
                print(f" {command}: {c_myFile} vs. {c_otherFile}")
        # exit()


if __name__ == "__main__":
    download_all_chapters()
    myFiles = get_list_of_my_chapter_files()
    compare_to_lang(myFiles=myFiles, lang=other_lang)
