"""Unit Tests."""  # noqa: INP001
# ruff: noqa: S101

from step_6 import fix_ellipsis

# quotations
assert fix_ellipsis("foo…”") == "foo…”"
assert fix_ellipsis("“…foo") == "“…foo"
# html
assert fix_ellipsis("foo…</p>") == "foo…</p>"
assert fix_ellipsis("<p>…foo") == "<p>…foo"
# between 2 words
assert fix_ellipsis("foo…bar") == "foo… bar"
assert fix_ellipsis("foo …bar") == "foo… bar"
assert fix_ellipsis("foo … bar") == "foo… bar"
assert fix_ellipsis("foo… bar") == "foo… bar"
# start of sentence
assert fix_ellipsis("foo.…bar") == "foo. …bar"
assert fix_ellipsis("foo!…bar") == "foo! …bar"
assert fix_ellipsis("foo?…bar") == "foo? …bar"
# end of sentence
assert fix_ellipsis("foo…. bar") == "foo…. bar"
assert fix_ellipsis("foo…! bar") == "foo…! bar"
assert fix_ellipsis("foo…? bar") == "foo…? bar"
