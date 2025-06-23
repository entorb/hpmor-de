# ruff: noqa: INP001, D103
# cspell:disable

"""Unit Tests."""

import sys
from pathlib import Path

import pytest
from step_6 import fix_ellipsis

sys.path.append(str(Path(__file__).resolve().parent.parent))
from check_chapters_settings import settings

LANG = settings["lang"]

if LANG == "EN":

    @pytest.mark.parametrize(
        ("text", "expected"),
        [
            # quotations
            ("foo…”", "foo…”"),
            ("“…foo", "“…foo"),
            # html
            ("foo…</p>", "foo…</p>"),
            ("<p>…foo", "<p>…foo"),
            # between 2 words
            ("foo…bar", "foo… bar"),
            ("foo …bar", "foo… bar"),
            ("foo … bar", "foo… bar"),
            ("foo… bar", "foo… bar"),
            # start of sentence
            ("foo.…bar", "foo. …bar"),
            ("foo!…bar", "foo! …bar"),
            ("foo?…bar", "foo? …bar"),
            # end of sentence
            ("foo…. bar", "foo…. bar"),
            ("foo…! bar", "foo…! bar"),
            ("foo…? bar", "foo…? bar"),
            # emph
            ("foo</em>…bar", "foo</em>… bar"),
            ("foo…<em>bar", "foo… <em>bar"),
        ],
    )
    def test_fix_ellipsis_en(text: str, expected: str) -> None:
        assert fix_ellipsis(text) == expected
