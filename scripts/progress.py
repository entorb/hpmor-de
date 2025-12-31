"""Statistics about translation progress."""

# ruff: noqa: E501 INP001
from pathlib import Path

last_done = 21

range_total = set(range(122 + 1))
print(range_total)

range_done = set(range(last_done + 1))
print(range_done)

bytes_total = 0
for i in range_total:
    path = Path(f"chapters/hpmor-chapter-{i:03}.tex")
    bytes_total += path.stat().st_size

bytes_done = 0
for i in range_done:
    path = Path(f"chapters/hpmor-chapter-{i:03}.tex")
    bytes_done += path.stat().st_size

print(
    f"Progress bytes: {bytes_done / bytes_total:.2%} ({bytes_done / 1024:.0f} / {bytes_total / 1024:.0f} kB)"
)
print(
    f"Progress chapters: {len(range_done) / len(range_total):.2%} ({len(range_done)} / {len(range_total)} chapters)"
)
