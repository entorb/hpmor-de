#!/usr/bin/env python3
"""
Download chapter files from the web.
"""

import os
import sys

import helper
import requests

# my helper

os.chdir(os.path.dirname(sys.argv[0]))

translations = helper.translations

# make output dirs
for translator in translations.keys():
    os.makedirs(f"1-download/{translator}/", exist_ok=True)


def download_file(url: str, filepath: str):
    """
    Download file from url to filepath.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0 ",  # noqa: E501
    }
    cont = requests.get(url, headers=headers, verify=True, timeout=3).content
    # verify=False -> skip SSL cert verification: CERTIFICATE_VERIFY_FAILED
    with open(filepath, mode="bw") as fh:
        fh.write(cont)


def download_all_chapters() -> None:
    """
    Download all chapters.

    downloads only if file does not exist yet
    """
    url_base = "https://www.fanfiktion.de/s/<---id--->/<---fileNum--->/"
    for translator, trans in translations.items():
        chapter = trans["chStart"]
        for fileNum in range(1, trans["numFiles"] + 1):
            fileOut = f"1-download/{translator}/%03d.html" % chapter
            if not os.path.exists(fileOut):
                print("downloading chapter %03d" % chapter)
                url = url_base.replace("<---id--->", trans["id"]).replace(
                    "<---fileNum--->",
                    str(fileNum),
                )
                download_file(url=url, filepath=fileOut)
            chapter += 1


if __name__ == "__main__":
    download_all_chapters()
