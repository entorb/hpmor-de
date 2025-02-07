# ruff: noqa: INP001 D103 RUF001 S101
"""Tests for check_chapters.py."""

from collections.abc import Callable

import pytest
from check_chapters import (
    fix_common_typos,
    fix_ellipsis,
    fix_emph,
    fix_hyphens,
    fix_latex,
    fix_line,
    fix_linebreaks_speech,
    fix_MrMrs,
    fix_numbers,
    fix_punctuation,
    fix_quotations,
    fix_spaces,
    fix_spell,
)
from check_chapters_settings import settings


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_common_typos(lang: str) -> None:
    settings["lang"] = lang
    pairs = [
        ("Test King's Cross", "Test King’s Cross"),
        ("Test", "Test"),
    ]
    if lang == "EN":
        pairs.extend(
            [
                ("I'm happy", "I’m happy"),
                ("can't be", "can’t be"),
            ]
        )
    elif lang == "DE":
        pairs.extend(
            [
                ("Junge-der-überlebt-hat", "Junge-der-überlebte"),
                ("Fritz'sche Gesetz", "Fritz’sche Gesetz"),
                ("Fritz'schen Gesetz", "Fritz’schen Gesetz"),
                ("Fritz'scher Gesetz", "Fritz’scher Gesetz"),
            ]
        )
    checkit(fix_common_typos, pairs)


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_ellipsis(lang: str) -> None:
    settings["lang"] = lang
    pairs = []
    if lang != "DE":
        pairs.extend(
            [
                ("foo...bar", "foo…bar"),
                ("foo…bar", "foo…bar"),
                ("foo … bar", "foo…bar"),
                ("foo… bar", "foo…bar"),
                ("foo …bar", "foo…bar"),
                ("foo, …", "foo, …"),
                ("foo …! bar", "foo…! bar"),
            ]
        )
    if lang == "DE":
        pairs.extend(
            [
                ("foo...bar", "foo … bar"),
                ("foo…bar", "foo … bar"),
                ("foo … bar", "foo … bar"),
                ("foo… bar", "foo … bar"),
                ("foo …bar", "foo … bar"),
                ("foo, …“", "foo, …“"),
                ("foo,…“", "foo, …“"),
                ("foo …! bar", "foo …! bar"),
                ("\\emph{…ihm", "\\emph{… ihm"),
            ]
        )

    checkit(fix_ellipsis, pairs)


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_emph(lang: str) -> None:
    settings["lang"] = lang
    pairs = [
        (r"That’s not \emph{true!}", r"That’s not \emph{true}!"),
        (r"she got \emph{magic,} can you", r"she got \emph{magic}, can you"),
        ("foo", "foo"),
    ]
    if lang == "EN":
        pairs.extend(
            [
                (r"briefly. \emph{Hopeless.} Both", r"briefly. \emph{Hopeless.} Both"),
                ("foo", "foo"),
            ]
        )
    elif lang == "DE":
        pairs.extend(
            [
                (r"briefly. \emph{Hopeless.} Both", r"briefly. \emph{Hopeless}. Both"),
                ("foo", "foo"),
            ]
        )
    checkit(fix_emph, pairs)


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_hyphens(lang: str) -> None:
    settings["lang"] = lang
    pairs = [
        ("2-3-4", "2–3–4"),
    ]
    if lang != "DE":
        pairs.extend(
            (
                (" —,", "—,"),
                (" —.", "—."),
                (" —!", "—!"),
                (" —?", "—?"),
                ("— foo", "—foo"),
                ("- foo", "—foo"),
                ("-foo", "—foo"),
            )
        )
    if lang == "DE":
        pairs.extend(
            (
                ("foo - bar", "foo — bar"),
                ("foo -- bar", "foo — bar"),
                ("foo --- bar", "foo — bar"),
                ("foo—bar", "foo — bar"),
                ("foo — bar", "foo — bar"),
                ("foo – bar", "foo — bar"),  # mid dash
                # quote start
                ("foo—„", "foo — „"),
                ("foo—‚", "foo — ‚"),
                ("foo —„", "foo — „"),
                ("foo „ —quote", "foo „— quote"),
                ("foo „ — quote", "foo „— quote"),
                ("foo—„— quote", "foo — „— quote"),
                # quote end
                ("quote —“foo", "quote —“ foo"),
                ("foo —“", "foo —“"),
                # emph
                ("\\emph{foo—}", "\\emph{foo —}"),
                ("\\emph{foo —}", "\\emph{foo —}"),
                ("\\emph{foo—} bar", "\\emph{foo —} bar"),
                ("foo—\\emph{bar}", "foo — \\emph{bar}"),
                ("\\emph{—ihm", "\\emph{— ihm"),
            )
        )
    checkit(fix_hyphens, pairs)


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_latex(lang: str) -> None:
    settings["lang"] = lang
    pairs = [
        ("begin at new line\\begin{em}", "begin at new line\n\\begin{em}"),
        ("end at new line\\end{em}", "end at new line\n\\end{em}"),
        ("new line after \\\\ foo", "new line after \\\\\nfoo"),
        ("no new line after \\\\", "no new line after \\\\"),
    ]
    checkit(fix_latex, pairs)


@pytest.mark.parametrize("lang", ["DE"])
def test_fix_linebreaks_speech(lang: str) -> None:
    settings["lang"] = lang
    pairs = [
        (" „Hello", "\n„Hello"),
        (" „hello", " „hello"),
        ("„hello", "„hello"),
    ]
    checkit(fix_linebreaks_speech, pairs)


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_MrMrs(lang: str) -> None:  # noqa: N802
    settings["lang"] = lang
    pairs = [
        ("Mr. H. Potter", "Mr~H.~Potter"),
        ("it’s Doctor now, not Miss.", "it’s Doctor now, not Miss."),
    ]
    if lang == "DE":
        pairs.extend(
            [
                ("Mr. Potter", "Mr~Potter"),
                ("Mrs. Potter", "Mrs~Potter"),
                ("Miss. Potter", "Miss~Potter"),
                ("Dr. Potter", "Dr~Potter"),
                ("Dr Potter", "Dr~Potter"),
                ("Mr Potter", "Mr~Potter"),
                ("Mr. and Mrs. Davis", "Mr~and Mrs~Davis"),
            ]
        )
    checkit(fix_MrMrs, pairs)


@pytest.mark.parametrize("lang", ["DE"])
def test_fix_numbers(lang: str) -> None:
    settings["lang"] = lang
    pairs = [
        ("Es ist 12:23 Uhr.", "Es ist 12:23~Uhr."),
    ]
    checkit(fix_numbers, pairs)


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_spaces(lang: str) -> None:
    settings["lang"] = lang
    pairs = [
        ("Hallo  Harry", "Hallo Harry"),
        ("tabs\tto\t\tspace", "tabs to space"),
        ("trailing spaces  ", "trailing spaces"),
        ("  ", ""),
        ("multiple  spaces", "multiple spaces"),
    ]
    checkit(fix_spaces, pairs)


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_punctuation(lang: str) -> None:
    settings["lang"] = lang
    pairs = [
        ("foo,, bar", "foo, bar"),
        ("foo.. bar", "foo. bar"),
        ("foo!! bar", "foo! bar"),
        ("foo?? bar", "foo? bar"),
        ("foo:: bar", "foo: bar"),
        ("foo;; bar", "foo; bar"),
    ]
    checkit(fix_punctuation, pairs)


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_quotations(lang: str) -> None:
    settings["lang"] = lang
    if settings["lang"] == "EN":
        pairs = [
            ('"foo"', "“foo”"),
            ("'foo'", "‘foo’"),
            (' "foo bar"', " “foo bar”"),
            # space at opening "
            ("“ foo ”", "“foo”"),
            ("\\emph{foo} ” bar", "\\emph{foo}” bar"),
            ("\\heading{“foo ”} bar", "\\heading{“foo”} bar"),
            ("\\emph{“foo”} bar", "“\\emph{foo}” bar"),
            ("\\emph{“ foo ”} bar", "“\\emph{foo}” bar"),
            ("\\emph{foo ”} bar", "\\emph{foo}” bar"),
            ("‘\\emph{foo}’", "‘foo’"),
        ]
    if settings["lang"] == "DE":
        pairs = [
            ('"foo"', "„foo“"),
            ("“foo”", "„foo“"),
            ("»foo«", "„foo“"),
            ("'foo'", "‚foo‘"),
            ("’foo‘", "‚foo‘"),
            (' "foo bar"', " „foo bar“"),
            ("…„", "… „"),
            ("„ foo “", "„foo“"),
            ("\\heading{„foo “} bar", "\\heading{„foo“} bar"),
            ("\\emph{„foo“} bar", "„\\emph{foo}“ bar"),
            ("\\emph{„ foo “} bar", "„\\emph{foo}“ bar"),
            ("\\emph{foo “} bar", "\\emph{foo}“ bar"),
            ("foo,“ bar", "foo“, bar"),
            ("‚\\emph{foo}‘", "‚foo‘"),
            ("„foo,“", "„foo“,"),
            ("„foo“bar", "„foo“ bar"),
            # EN closing
            ("„foo”", "„foo“"),
        ]
    checkit(fix_quotations, pairs)


@pytest.mark.parametrize("lang", ["DE"])
def test_fix_spell(lang: str) -> None:
    settings["lang"] = lang
    pairs = [
        ("‚Lumos‘", "\\spell{Lumos}"),
        ("„Lumos“", "\\spell{Lumos}"),
        ("„\\emph{Lumos}“", "\\spell{Lumos}"),
        ("\\emph{„Lumos“}", "\\spell{Lumos}"),
        ("\\emph{Lumos!}", "\\spell{Lumos}"),
        ("„\\spell{Lumos}“", "\\spell{Lumos}"),
    ]
    checkit(fix_spell, pairs)


def checkit(fct: Callable, pairs: list[tuple[str, str]]) -> None:
    for text, expected_output in pairs:
        # test of isolated function
        assert fct(text) == expected_output, (
            f"'{text}' -> '{fct(text)}' != '{expected_output}'"
        )

        # test in complete fix_line context
        assert fix_line(text) == expected_output, (
            f"'{text}' -> '{fix_line(text)}' != '{expected_output}' (fix_line)"
        )
