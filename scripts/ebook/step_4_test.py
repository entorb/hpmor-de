# ruff: noqa: INP001 S101
# cspell:disable

"""Unit Tests."""

import pytest
from step_4 import convert_parsel


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("foo", "foo"),
        # s
        ("house", "housse"),
        ("Special", "Sspecial"),
        # ss and ß
        ("Professor", "Professsor"),
        ("muß", "musss"),
        # z
        ("zero", "zzero"),
        ("Zero", "Zzero"),
        # zz
        ("puzzled", "puzzzled"),
        # x -> xs
        ("Bellatrix", "Bellatrixs"),
        # combined
        ("expression", "exspresssion"),
        ("Salazar", "Ssalazzar"),
    ],
)
def test_convert_parsel(text: str, expected: str) -> None:  # noqa: D103
    assert convert_parsel(text) == expected
