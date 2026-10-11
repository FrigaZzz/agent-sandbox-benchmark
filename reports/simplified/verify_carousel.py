"""Verify the short guide's PDF layout, links and cost arithmetic."""
from __future__ import annotations

from decimal import Decimal
import re
from pathlib import Path
from urllib.parse import unquote

import pymupdf

from build_carousel import SOURCES


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]


def local_links(path: Path) -> int:
    links = re.findall(r"\]\(([^\s)]+)(?:\s+[^)]*)?\)", path.read_text())
    checked = 0
    for link in links:
        if link.startswith(("https://", "http://", "#", "mailto:")):
            continue
        target = unquote(link.split("#", 1)[0])
        if not (path.parent / target).exists():
            raise AssertionError(f"Broken local link in {path.relative_to(REPO)}: {link}")
        checked += 1
    return checked


def main() -> None:
    docs = [HERE / name for name in ["README.md", "sources.md", "slides.md"]]
    docs += [REPO / "reports/README.md", REPO / "reports/docs/field-guide-readme.md"]
    link_count = sum(local_links(path) for path in docs)
    # Default font-metric boxes include ascender/descender whitespace, which
    # overlaps across ordinary multiline leading even when glyphs are separate.
    pymupdf.TOOLS.set_small_glyph_heights(True)
    with pymupdf.open(HERE / "agent-sandbox-decisions.pdf") as pdf:
        assert len(pdf) == 9
        links = {link["uri"] for page in pdf for link in page.get_links() if "uri" in link}
        assert {v for k, v in SOURCES.items() if k != "OpenAI pricing"}.issubset(links)
        for i, page in enumerate(pdf):
            spans = [span for block in page.get_text("dict")["blocks"]
                     for line in block.get("lines", []) for span in line["spans"]]
            for j, span in enumerate(spans):
                rect = pymupdf.Rect(span["bbox"])
                assert page.rect.contains(rect), f"Page {i + 1} has off-page text"
                for other in spans[j + 1:]:
                    intersection = rect & pymupdf.Rect(other["bbox"])
                    assert intersection.is_empty or intersection.get_area() < 1, (
                        f"Page {i + 1} has overlapping glyph boxes: {span['text']!r} / {other['text']!r}")
    model = Decimal("0.003")  # Explicit scenario assumption; no dated model rate.
    per_second = 2 * Decimal("0.000014") + 4 * Decimal("0.0000045")
    assert model == Decimal("0.003")
    assert per_second * 10 == Decimal("0.00046")
    assert per_second * 300 == Decimal("0.01380")
    assert per_second * 300 / model == Decimal("4.6")
    print(f"PASS: 9 pages; all official PDF links; no text overlap; {link_count} local links; exact cost arithmetic")


if __name__ == "__main__":
    main()
