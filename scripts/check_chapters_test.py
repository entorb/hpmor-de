"""Tests for check_chapters.py ."""  # noqa: INP001

# ruff: noqa: S101 RUF001 RUF003 D103

from check_chapters import (
    fix_common_typos,
    fix_ellipsis,
    fix_emph,
    fix_hyphens,
    fix_latex,
    fix_line,
    fix_linebreaks_speach,
    fix_MrMrs,
    fix_numbers,
    fix_punctuation,
    fix_spaces,
    fix_spell,
)
from check_chapters_settings import settings

# TODO: loop
settings["lang"] = "EN"
#
# fix_spaces
#
for text, expected_output in [
    ("Hallo  Harry", "Hallo Harry"),
    ("tabs\tto\t\tspace", "tabs to space"),
    ("trailing spaces  ", "trailing spaces"),
    ("  ", ""),
    ("multiple  spaces", "multiple spaces"),
]:
    assert (
        fix_spaces(s=text) == expected_output
    ), f"'{fix_spaces(s=text)}' != '{expected_output}'"
    assert (
        fix_line(s=text) == expected_output
    ), f"'{fix_line(s=text)}' != '{expected_output}'"

#
# fix_punctuation
#
for text, expected_output in [
    ("!!", "!"),
    ("??", "?"),
    ("! !", "!"),
    ("..", "."),
    (",,", ","),
]:
    assert (
        fix_punctuation(s=text) == expected_output
    ), f"'{fix_punctuation(s=text)}' != '{expected_output}'"
    assert (
        fix_line(s=text) == expected_output
    ), f"'{fix_line(s=text)}' != '{expected_output}'"

#
# fix_latex
#
for text, expected_output in [
    ("begin at new line\\begin{em}", "begin at new line\n\\begin{em}"),
    ("end at new line\\end{em}", "end at new line\n\\end{em}"),
    ("new line after \\\\ asdf", "new line after \\\\\nasdf"),
    ("no new line after \\\\", "no new line after \\\\"),
]:
    assert (
        fix_latex(s=text) == expected_output
    ), f"'{fix_latex(s=text)}' != '{expected_output}'"
    assert (
        fix_line(s=text) == expected_output
    ), f"'{fix_line(s=text)}' != '{expected_output}'"

#
# fix_ellipsis#
#
assert fix_ellipsis("foo...bar") == "foo…bar"
assert fix_ellipsis("foo … bar") == "foo…bar"
assert fix_ellipsis("foo… bar") == "foo…bar"
assert fix_ellipsis("foo …bar") == "foo…bar"
assert fix_ellipsis("foo, …") == "foo, …"
for text, expected_output in [
    ("foo…bar", "foo…bar"),
    ("foo … bar", "foo…bar"),
    ("foo… bar", "foo…bar"),
    ("foo …bar", "foo…bar"),
    ("foo, …", "foo, …"),
]:
    assert (
        fix_ellipsis(s=text) == expected_output
    ), f"'{fix_ellipsis(s=text)}' != '{expected_output}'"
    assert (
        fix_line(s=text) == expected_output
    ), f"'{fix_line(s=text)}' != '{expected_output}'"

#
# fix_numbers
#
if settings["lang"] == "DE":
    assert fix_numbers("Es ist 12:23 Uhr...") == "Es ist 12:23~Uhr..."
#
# fix_MrMrs
#
assert fix_MrMrs("Mr. H. Potter") == "Mr~H.~Potter"
pairs = [
    ("Mr. H. Potter", "Mr~H.~Potter"),
    ("it’s Doctor now, not Miss.", "it’s Doctor now, not Miss."),
]
if settings["lang"] == "DE":
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
for text, expected_output in pairs:
    assert (
        fix_MrMrs(s=text) == expected_output
    ), f"'{fix_MrMrs(s=text)}' != '{expected_output}'"
    assert (
        fix_line(s=text) == expected_output
    ), f"'{fix_line(s=text)}' != '{expected_output}'"

#
# fix_common_typos
#
pairs = [
    ("Test Mungo's King's Cross", "Test Mungo’s King’s Cross"),
    ("asdf", "asdf"),
]
if settings["lang"] == "DE":
    pairs.extend(
        [
            ("Junge-der-überlebt-hat", "Junge-der-überlebte"),
            ("Fritz'sche Gesetz", "Fritz’sche Gesetz"),
            ("Fritz'schen Gesetz", "Fritz’schen Gesetz"),
            ("Fritz'scher Gesetz", "Fritz’scher Gesetz"),
        ]
    )
if settings["lang"] == "EN":
    pairs.extend(
        [
            ("I'm happy", "I’m happy"),
            ("can't be", "can’t be"),
        ]
    )
for text, expected_output in pairs:
    assert (
        fix_common_typos(s=text) == expected_output
    ), f"'{fix_common_typos(s=text)}' != '{expected_output}'"
    assert (
        fix_line(s=text) == expected_output
    ), f"'{fix_line(s=text)}' != '{expected_output}'"

# fix_emph
pairs = [
    (r"That’s not \emph{true!}", r"That’s not \emph{true}!"),
    (r"she got \emph{magic,} can you", r"she got \emph{magic}, can you"),
    ("asdf", "asdf"),
]
if settings["lang"] == "DE":
    pairs.extend(
        [
            (
                r"briefly. \emph{Hopeless.} Both",
                r"briefly. \emph{Hopeless}. Both",  # . now out
            ),
            ("asdf", "asdf"),
        ]
    )
if settings["lang"] == "EN":
    pairs.extend(
        [
            (
                r"briefly. \emph{Hopeless.} Both",
                r"briefly. \emph{Hopeless.} Both",  # . unchanged
            ),
            ("asdf", "asdf"),
        ]
    )
for text, expected_output in pairs:
    assert (
        fix_emph(s=text) == expected_output
    ), f"'{fix_emph(s=text)}' != '{expected_output}'"
    assert (
        fix_line(s=text) == expected_output
    ), f"'{fix_line(s=text)}' != '{expected_output}'"


#
# fix_hyphens
#
pairs = [
    ("2-3-4", "2–3–4"),
    (" —,", "—,"),
    (" —.", "—."),
    (" —!", "—!"),
    (" —?", "—?"),
    # start of line
    ("— asdf", "—asdf"),
    ("- asdf", "—asdf"),
    ("-asdf", "—asdf"),
]
if settings["lang"] == "DE":
    pairs.extend(
        [
            # end of line
            ("Text —", "Text—"),
            # start of quote
            ("Text—„", "Text— „"),
            ("Text —„", "Text— „"),
            ("Text „ —Quote", "Text „—Quote"),
            ("Text „ — Quote", "Text „—Quote"),
            ("Text—„— Quote", "Text— „—Quote"),
            # end of quote
            ("Text -“asdf", "Text—“ asdf"),
            ("Text —“", "Text—“"),
        ]
    )
for text, expected_output in pairs:
    assert (
        fix_hyphens(s=text) == expected_output
    ), f"'{fix_hyphens(s=text)}' != '{expected_output}'"
    assert (
        fix_line(s=text) == expected_output
    ), f"'{fix_line(s=text)}' != '{expected_output}'"


#
# fix_spell
#

if settings["lang"] == "EN":
    pairs = [
        (r"‘Lumos’", r"‘Lumos’"),
        ("asdf", "asdf"),
    ]
if settings["lang"] == "DE":
    pairs = [
        (r"‚Lumos‘", r"\spell{Lumos}"),
        (r"„Lumos“", r"\spell{Lumos}"),
        (r"„\emph{Lumos}“", r"\spell{Lumos}"),
        (r"\emph{„Lumos“}", r"\spell{Lumos}"),
        (r"\emph{Lumos!}", r"\spell{Lumos}"),
        (r"„\spell{Lumos}“", r"\spell{Lumos}"),
    ]
for text, expected_output in pairs:
    assert (
        fix_spell(s=text) == expected_output
    ), f"'{fix_spell(s=text)}' != '{expected_output}'"
    assert (
        fix_line(s=text) == expected_output
    ), f"'{fix_line(s=text)}' != '{expected_output}'"


#
# fix_linebreaks_speach
#
if settings["lang"] == "DE":
    pairs = [
        (" „Hello", "\n„Hello"),
        (" „hello", " „hello"),
        ("„hello", "„hello"),
    ]
    for text, expected_output in pairs:
        assert (
            fix_linebreaks_speach(s=text) == expected_output
        ), f"'{fix_linebreaks_speach(s=text)}' != '{expected_output}'"
        assert (
            fix_line(s=text) == expected_output
        ), f"'{fix_line(s=text)}' != '{expected_output}'"
