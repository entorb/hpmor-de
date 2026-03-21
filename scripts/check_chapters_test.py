# ruff: noqa: D103, RUF001
"""Tests for check_chapters.py."""

from collections.abc import Callable
from pathlib import Path

import pytest

from .check_chapters import (
    fix_common_typos,
    fix_ellipsis,
    fix_emph,
    fix_hyphens,
    fix_latex,
    fix_line,
    fix_linebreaks_speech,
    fix_mr_mrs,
    fix_numbers,
    fix_punctuation,
    fix_quotations,
    fix_spaces,
    fix_spell,
    get_list_of_chapter_files,
    multiline_check,
    process_file,
)
from .check_chapters_settings import settings


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_common_typos(lang: str) -> None:
    settings["lang"] = lang
    pairs = [
        ("Test King’s Cross", "Test King’s Cross"),
        ("Test", "Test"),
    ]
    if lang == "EN":
        pairs.extend(
            [
                ("I’m happy", "I’m happy"),
                ("can’t be", "can’t be"),
            ]
        )
    elif lang == "DE":
        # cspell:disable
        pairs.extend(
            [
                ("Junge-der-überlebt-hat", "Junge-der-überlebte"),
                ("Junge-der-überlebt-hatte", "Junge-der-überlebte"),
                ("Jungen-der-überlebt-hat", "Jungen-der-überlebte"),
                ("Junge, der lebte", "Junge-der-überlebte"),
                ("Fritz'sche Gesetz", "Fritz’sche Gesetz"),
                ("Fritz'schen Gesetz", "Fritz’schen Gesetz"),
                ("Fritz'scher Gesetz", "Fritz’scher Gesetz"),
                ("Galeone", "Galleone"),
                ("Galeonen", "Galleonen"),
                ("Galleone", "Galleone"),
                ("Hermione", "Hermine"),
                ("Wizengamot", "Zaubergamot"),
                ("Stupefy", "Stupor"),
                ("ut mir Leid", "ut mir leid"),
                ("stellvertretende Schulleiterin", "Stellvertretende Schulleiterin"),
            ]
            # cspell:enable
        )
    check_it(fix_common_typos, pairs)


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_ellipsis(lang: str) -> None:
    settings["lang"] = lang
    pairs = []
    if lang != "DE":
        # cspell:disable
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
        # cspell:enable
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
                # …“Text -> …“ Text
                ("foo …“bar", "foo …“ bar"),
            ]
        )

    check_it(fix_ellipsis, pairs)


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
                # space at start of emph moves before
                (r"foo\emph{ bar}", r"foo \emph{bar}"),
                ("foo", "foo"),
            ]
        )
    check_it(fix_emph, pairs)
    if lang == "DE":
        # ellipsis inside emph: fix_emph alone should not move it out
        # (fix_ellipsis handles spacing separately in fix_line)
        assert fix_emph(r"\emph{foo…}") == r"\emph{foo…}"


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
                ("2 – 4", "2–4"),  # en-dash number range preserved
                ("10 – 20", "10–20"),
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
    check_it(fix_hyphens, pairs)


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_latex(lang: str) -> None:
    settings["lang"] = lang
    pairs = [
        ("begin at new line\\begin{em}", "begin at new line\n\\begin{em}"),
        ("end at new line\\end{em}", "end at new line\n\\end{em}"),
        ("new line after \\\\ foo", "new line after \\\\\nfoo"),
        ("no new line after \\\\", "no new line after \\\\"),
    ]
    if lang == "DE":
        pairs.extend(
            [
                ("foo\\translatorsnote", "foo%\n\\translatorsnote"),
            ]
        )
    check_it(fix_latex, pairs)


@pytest.mark.parametrize("lang", ["DE"])
def test_fix_linebreaks_speech(lang: str) -> None:
    settings["lang"] = lang
    pairs = [
        (" „Hello", "\n„Hello"),
        (" „hello", " „hello"),
        ("„hello", "„hello"),
        # macro triggers
        (" „\\emph{foo}", "\n„\\emph{foo}"),
        (" „\\shout{foo}", "\n„\\shout{foo}"),
    ]
    check_it(fix_linebreaks_speech, pairs)
    # These macros interact with fix_spell/fix_quotations in fix_line context,
    # so test in isolation only
    isolated_pairs = [
        (" „\\spell{foo}", "\n„\\spell{foo}"),
        (" „\\scream{foo}", "\n„\\scream{foo}"),
        (" „\\prophesy{foo}", "\n„\\prophesy{foo}"),
    ]
    for text, expected in isolated_pairs:
        assert fix_linebreaks_speech(text) == expected, (
            f"'{text}' -> '{fix_linebreaks_speech(text)}' != '{expected}'"
        )


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_mr_mrs(lang: str) -> None:
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
    check_it(fix_mr_mrs, pairs)


@pytest.mark.parametrize("lang", ["DE"])
def test_fix_numbers(lang: str) -> None:
    settings["lang"] = lang
    pairs = [
        ("Es ist 12:23 Uhr.", "Es ist 12:23~Uhr."),
    ]
    check_it(fix_numbers, pairs)


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
    check_it(fix_spaces, pairs)


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
    check_it(fix_punctuation, pairs)


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_fix_quotations(lang: str) -> None:
    settings["lang"] = lang
    if settings["lang"] == "EN":
        pairs = [
            ('"foo"', "“foo”"),
            ("'foo'", "‘foo’"),
            (' "foo bar"', " “foo bar”"),
            # space at opening “
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
            ("‘foo’", "‚foo‘"),
            (' "foo bar"', " „foo bar“"),
            ("…„", "… „"),
            ("„ foo “", "„foo“"),
            ("\\heading{„foo “} bar", "\\heading{„foo“} bar"),
            ("\\emph{„foo“} bar", "„\\emph{foo}“ bar"),
            ("\\emph{„ foo “} bar", "„\\emph{foo}“ bar"),
            ("\\emph{foo “} bar", "\\emph{foo}“ bar"),
            ("foo,“ bar", "foo“, bar"),
            ("‚\\emph{foo}‘", "‚foo‘"),
            ("\\emph{‚foo‘}", "‚foo‘"),
            ("„foo,“", "„foo“,"),
            ("„foo“bar", "„foo“ bar"),
            # EN closing
            ("„foo”", "„foo“"),
        ]
    check_it(fix_quotations, pairs)


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
        # Finite Incantatem matched before Finite
        ("„Finite Incantatem“", "\\spell{Finite Incantatem}"),
        ("„Finite“", "\\spell{Finite}"),
        # spell cleanup: no ! inside or after
        ("\\spell{Lumos!}", "\\spell{Lumos}"),
        ("\\spell{Lumos}!", "\\spell{Lumos}"),
    ]
    check_it(fix_spell, pairs)


@pytest.mark.parametrize("lang", ["EN", "DE"])
def test_multiline_check(lang: str) -> None:
    settings["lang"] = lang
    # CRLF -> LF
    assert multiline_check("foo\r\nbar") == "foo\nbar"
    # CR -> LF
    assert multiline_check("foo\rbar") == "foo\nbar"
    # triple newlines collapsed
    assert multiline_check("foo\n\n\nbar") == "foo\n\nbar"
    if lang == "DE":
        # line before translatorsnote must end with %
        assert multiline_check("foo\n\\translatorsnote") == "foo%\n\\translatorsnote"


@pytest.mark.parametrize("lang", ["EN"])
def test_fix_spell_en(lang: str) -> None:
    settings["lang"] = lang
    # EN: early return, no spell macro in EN yet
    assert fix_spell("'Lumos'") == "'Lumos'"
    # EN: non-spell text unchanged
    assert fix_spell("hello world") == "hello world"


@pytest.mark.parametrize("lang", ["EN"])
def test_fix_linebreaks_speech_en(lang: str) -> None:
    settings["lang"] = lang
    # EN: no-op, returns input unchanged
    assert fix_linebreaks_speech("foo bar") == "foo bar"
    assert fix_linebreaks_speech(" „Hello") == " „Hello"


def test_get_list_of_chapter_files() -> None:
    files = get_list_of_chapter_files()
    assert len(files) > 0
    assert all(f.suffix == ".tex" for f in files)
    assert all(f.is_file() for f in files)


@pytest.mark.parametrize("lang", ["DE"])
def test_process_file_no_issues(lang: str, tmp_path: Path) -> None:
    settings["lang"] = lang
    settings["inline_fixing"] = False
    settings["print_diff"] = False
    # file with no issues
    test_file = tmp_path / "test-chapter.tex"
    test_file.write_text("Hallo Welt.\n", encoding="utf-8")
    result = process_file(test_file)
    assert result is False


@pytest.mark.parametrize("lang", ["DE"])
def test_process_file_with_issues(lang: str, tmp_path: Path) -> None:
    settings["lang"] = lang
    settings["inline_fixing"] = False
    settings["print_diff"] = False
    # file with fixable issues: double spaces
    test_file = tmp_path / "test-chapter.tex"
    test_file.write_text("Hallo  Welt.\n", encoding="utf-8")
    result = process_file(test_file)
    assert result is True
    # autofix file should exist
    autofix = tmp_path / "test-chapter-autofix.tex"
    assert autofix.is_file()


@pytest.mark.parametrize("lang", ["DE"])
def test_process_file_inline_fixing(lang: str, tmp_path: Path) -> None:
    settings["lang"] = lang
    settings["inline_fixing"] = True
    settings["print_diff"] = False
    test_file = tmp_path / "test-chapter.tex"
    test_file.write_text("Hallo  Welt.\n", encoding="utf-8")
    result = process_file(test_file)
    # inline_fixing sets issues_found to False
    assert result is False
    # original file should be modified
    content = test_file.read_text(encoding="utf-8")
    assert "  " not in content


@pytest.mark.parametrize("lang", ["DE"])
def test_process_file_with_diff(lang: str, tmp_path: Path) -> None:
    settings["lang"] = lang
    settings["inline_fixing"] = False
    settings["print_diff"] = True
    test_file = tmp_path / "test-chapter.tex"
    test_file.write_text("Hallo  Welt.\n", encoding="utf-8")
    result = process_file(test_file)
    assert result is True


@pytest.mark.parametrize("lang", ["DE"])
def test_process_file_commented_lines(lang: str, tmp_path: Path) -> None:
    settings["lang"] = lang
    settings["inline_fixing"] = False
    settings["print_diff"] = False
    # commented lines should be preserved as-is
    test_file = tmp_path / "test-chapter.tex"
    test_file.write_text("% This  has  double  spaces\nHallo Welt.\n", encoding="utf-8")
    result = process_file(test_file)
    assert result is False


@pytest.mark.parametrize("lang", ["DE"])
def test_process_file_multiline_issues(lang: str, tmp_path: Path) -> None:
    settings["lang"] = lang
    settings["inline_fixing"] = False
    settings["print_diff"] = False
    # triple newlines should be collapsed
    test_file = tmp_path / "test-chapter.tex"
    test_file.write_text("Hallo\n\n\nWelt.\n", encoding="utf-8")
    result = process_file(test_file)
    assert result is True


def check_it(fct: Callable, pairs: list[tuple[str, str]]) -> None:
    for text, expected_output in pairs:
        # test of isolated function
        assert fct(text) == expected_output, (
            f"'{text}' -> '{fct(text)}' != '{expected_output}'"
        )

        # test in complete fix_line context
        assert fix_line(text) == expected_output, (
            f"'{text}' -> '{fix_line(text)}' != '{expected_output}' (fix_line)"
        )
