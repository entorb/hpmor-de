# ruff: noqa: INP001 S101 D103
# cspell:disable

"""Unit Tests."""
# ruff: noqa: S101

import pytest
from step_6 import fix_ellipsis


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
def test_fix_ellipsis(text: str, expected: str) -> None:
    assert fix_ellipsis(text) == expected
