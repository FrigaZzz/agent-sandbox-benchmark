"""Build the short, vector-based PDF and its readable transcript.

Requires PyMuPDF and Pillow (the repository's presentation dependencies).
Run from any directory. Public resource URLs are optional and never inferred.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlparse

import pymupdf as fitz
from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent
W, H = 1080, 1350
INK = "#172B32"
PAPER = "#F5F3EA"
MUTED = "#4C6066"
GREEN = "#CCEE7B"
PALE = "#E7ECDf"
WHITE = "#FFFFFF"
ORANGE = "#F2C9A2"

SOURCES = {
    "Google release": "https://docs.cloud.google.com/gemini-enterprise-agent-platform/release-notes#September_09_2026",
    "Databricks news": "https://www.databricks.com/blog/agent-bricks-dais-2026",
    "Theo's video": "https://www.youtube.com/watch?v=vRS2leJLAI0",
    "Stanford AI Index": "https://hai.stanford.edu/ai-index/2025-ai-index-report",
    "Memory forecast": "https://www.trendforce.com/presscenter/news/20260930-13258.html",
    "Hetzner prices": "https://docs.hetzner.com/general/infrastructure-and-availability/price-adjustment/#cloud-servers",
    "E2B persistence": "https://docs.e2b.dev/sandbox/persistence.md",
    "E2B GPU FAQ": "https://docs.e2b.dev/faq/gpu-support.md",
    "Modal resources": "https://modal.com/docs/guide/sandbox-resources",
    "Daytona regions": "https://www.daytona.io/docs/en/regions.md",
    "Modal residency": "https://modal.com/docs/guide/data-residency",
    "E2B pricing": "https://e2b.dev/pricing",
    "OpenAI pricing": "https://developers.openai.com/api/docs/models/gpt-4o-mini",
}


def rgb(hex_color: str) -> tuple[float, float, float]:
    return tuple(int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))


class Carousel:
    def __init__(self) -> None:
        self.doc = fitz.open()
        self.transcript: list[str] = []
        self.manifest: list[dict] = []

    def page(self, section: str, *, dark: bool = False) -> None:
        self.p = self.doc.new_page(width=W, height=H)
        self.dark = dark
        self.fg = PAPER if dark else INK
        self.bg = INK if dark else PAPER
        self.box(0, 0, W, H, self.bg)
        self.transcript.append(f"\n## {len(self.doc)}. {section}\n")
        self.manifest.append({"page": len(self.doc), "section": section, "text_boxes": [], "links": []})
        self.text(72, 55, 880, 55, "AGENT SANDBOXES / DECISION NOTES", 28,
                  color=GREEN if dark else MUTED, bold=True, record=False)
        self.box(72, 1230, 936, 2, MUTED)
        self.text(72, 1260, 820, 45, "EVIDENCE + SOURCES / 13 OCT 2026", 27,
                  color=PAPER if dark else MUTED, record=False)
        self.text(910, 1255, 98, 50, f"{len(self.doc):02d} / 09", 28,
                  color=self.fg, record=False)

    def box(self, x: float, y: float, w: float, h: float, color: str) -> None:
        self.p.draw_rect(fitz.Rect(x, y, x + w, y + h), color=None, fill=rgb(color), overlay=True)

    def line(self, x1: float, y1: float, x2: float, y2: float, color: str = MUTED) -> None:
        self.p.draw_line((x1, y1), (x2, y2), color=rgb(color), width=3)

    def text(self, x: float, y: float, w: float, h: float, value: str, size: float = 46,
             *, color: str | None = None, bold: bool = False, record: bool = True) -> None:
        rect = fitz.Rect(x, y, x + w, y + h)
        if rect.x0 < 0 or rect.y0 < 0 or rect.x1 > W or rect.y1 > H:
            raise ValueError(f"Text box outside page: {value!r}")
        spare = self.p.insert_textbox(rect, value, fontsize=size,
                                      fontname="hebo" if bold else "helv",
                                      color=rgb(color or self.fg), lineheight=1.12)
        if spare < 0:
            raise ValueError(f"Page {len(self.doc)} text overflows by {-spare:.1f}pt: {value!r}")
        self.manifest[-1]["text_boxes"].append({"text": value, "rect": list(rect), "font_size": size})
        if record:
            self.transcript.append(value.replace("\n", " ") + "\n")

    def title(self, value: str, *, size: float = 80) -> None:
        self.text(72, 154, 936, 265, value, size, bold=True)

    def label(self, value: str, y: float, *, color: str = MUTED) -> None:
        self.text(72, y, 936, 44, value, 30, color=color, bold=True)

    def source(self, label: str, x: float, y: float, w: float) -> None:
        self.text(x, y, w, 45, label, 29, color=self.fg, bold=True, record=False)
        url = SOURCES[label]
        rect = fitz.Rect(x, y, x + w, y + 45)
        self.p.insert_link({"kind": fitz.LINK_URI, "from": rect, "uri": url})
        self.manifest[-1]["links"].append(url)
        self.transcript.append(f"Source: [{label}]({url})\n")


def build(github_url: str | None, medium_url: str | None) -> Carousel:
    c = Carousel()

    c.page("Cheaper AI, what about the machines?", dark=True)
    c.text(72, 168, 936, 385, "Cheaper AI.\nWhat about\nthe machines?", 102, bold=True)
    c.box(72, 553, 120, 12, GREEN)
    c.text(72, 618, 936, 185, "Why I revisited\nagent sandboxes.", 58, color=GREEN)
    for x, name, detail in [(72, "MODEL", "instructions"), (390, "MACHINE", "execution"),
                            (708, "RESULT", "verified output")]:
        c.box(x, 875, 300, 180, "#284149")
        c.text(x + 24, 903, 255, 58, name, 35, color=GREEN, bold=True)
        c.text(x + 24, 974, 255, 58, detail, 32, color=PAPER)
    c.text(72, 1100, 936, 85, "Cost, privacy, features and customization.", 42)

    c.page("The news that reopened the choice")
    c.title("New sandboxes.\nArchitecture rethink.")
    for y, name, body, source in [
        (430, "GOOGLE / 9 SEPTEMBER 2026",
         "Shell + computer-use sandboxes reach GA.\nPause idle compute while preserving files.", "Google release"),
        (745, "DATABRICKS / 16 JUNE 2026",
         "Sandbox announced within Agent Bricks.\nDedicated offering currently no-charge Beta.", "Databricks news"),
    ]:
        c.box(72, y, 936, 280, WHITE)
        c.text(100, y + 22, 880, 60, name, 32, color=MUTED, bold=True)
        c.text(100, y + 90, 880, 135, body, 40)
        c.source(source, 100, y + 230, 500)
    c.text(72, 1063, 936, 150, "These developments prompted my side-project\narchitecture review, mainly around cost.\nNew features aren't benchmark results.", 39)

    c.page("State is three contracts")
    c.title("What survives?")
    c.text(72, 290, 936, 130, "Files, durable disk and memory\nare separate promises.", 47)
    for y, number, name, body in [
        (435, "01", "BETWEEN CALLS", "Can the next call read the files?"),
        (608, "02", "AFTER STOP", "Does disk remain? For how long?"),
        (781, "03", "ON RESUME", "Are variables and processes restored?"),
    ]:
        c.box(72, y, 936, 149, WHITE)
        c.text(95, y + 25, 85, 95, number, 54, color=MUTED, bold=True)
        c.text(204, y + 16, 770, 46, name, 29, color=MUTED, bold=True)
        c.text(204, y + 68, 770, 73, body, 40)
    c.text(72, 972, 936, 103, "E2B documents memory + files on default pause.\nOur E2B/Modal checks verified files across calls.", 39)
    c.text(72, 1085, 936, 64, "Stop/resume was not tested in this pilot.", 39, bold=True)
    c.source("E2B persistence", 72, 1170, 470)

    c.page("Image and hardware")
    c.title("Bring your tools.\nChoose the hardware.")
    for x, name, body in [(72, "IMAGE", "Libraries\nand toolchain"),
                           (552, "ALLOCATION", "CPU, RAM\nand device")]:
        c.box(x, 415, 456, 245, GREEN if x == 552 else WHITE)
        c.text(x + 28, 440, 400, 58, name, 36, color=MUTED, bold=True)
        c.text(x + 28, 512, 400, 137, body, 49, bold=True)
    for y, name, body in [(713, "E2B", "Templates; CPU-only sandboxes."),
                           (822, "MODAL", "GPU offered; plan for interruptions."),
                           (931, "DAYTONA", "Shared GPU placement ignores preference.")]:
        c.text(72, y, 220, 70, name, 36, color=MUTED, bold=True)
        c.text(290, y, 718, 105, body, 40)
    c.text(72, 1053, 936, 105, "Check the exact runtime class and controls.\nGPU configurations were not benchmarked here.", 39)
    c.source("E2B GPU FAQ", 72, 1170, 280)
    c.source("Modal resources", 372, 1170, 310)
    c.source("Daytona regions", 712, 1170, 296)

    c.page("The whole data map")
    c.title("An EU region is\none part of the map.")
    c.label("MODAL EXAMPLE / DOCUMENTED DATA LOCATIONS", 415)
    c.box(72, 492, 395, 490, GREEN)
    c.text(108, 528, 323, 130, "COMPUTE\nEEA-pinned", 48, bold=True)
    c.text(108, 700, 323, 220, "EEA is broader\nthan the EU.\nPinning covers\ncompute.", 40)
    for y, name, body in [(492, "LOGS", "US stdout / stderr"),
                           (665, "SNAPSHOTS", "US, when created"),
                           (838, "MANAGED STORAGE", "US durable products")]:
        c.line(467, y + 69, 545, y + 69)
        c.box(545, y, 463, 144, WHITE)
        c.text(571, y + 16, 410, 46, name, 31, color=MUTED, bold=True)
        c.text(571, y + 66, 410, 70, body, 38)
    c.text(72, 1021, 936, 150, "Also trace backups, control-plane data, support\naccess and model calls. A model endpoint\nhas its own processing boundary.", 40)
    c.source("Modal residency", 72, 1180, 450)

    c.page("Two different economic trends")
    c.title("The machines have\ntheir own economics.")
    c.box(72, 424, 936, 310, GREEN)
    c.text(100, 450, 880, 62, "CHEAPER ACCESS TO CAPABILITY", 33, color=MUTED, bold=True)
    c.text(100, 510, 880, 125, "280-fold+", 86, bold=True)
    c.text(100, 633, 880, 104, "GPT-3.5-level inference cost drop.\nNov 2022 to Oct 2024 (Stanford AI Index).", 39)
    c.box(72, 774, 936, 325, WHITE)
    c.text(100, 799, 880, 65, "2026 INFRASTRUCTURE PRICE PRESSURE", 33, color=MUTED, bold=True)
    c.text(100, 873, 880, 188, "Server memory supply remains tight.\nTrendForce forecasts further price rises.\nHetzner raised new-order cloud prices in June.", 39)
    c.text(72, 1113, 936, 55, "These are different markets and time periods.", 36, color=MUTED)
    c.source("Stanford AI Index", 72, 1180, 310)
    c.source("Memory forecast", 397, 1180, 310)
    c.source("Hetzner prices", 722, 1180, 286)

    c.page("Economics")
    c.title("Cheaper tokens.\nStill a machine bill.")
    c.text(72, 395, 936, 110, "Same model budget. Different billed running time.\nHypothetical USD usage, before credits.", 40)
    c.label("MODEL-AGNOSTIC SCENARIO / NOT A MODEL RATE", 525)
    c.text(72, 579, 936, 70, "Assumed model budget: $0.003 in both", 46, bold=True)
    c.label("E2B: 2 VCPU + 4 GIB / BILLED RUNNING TIME", 684)
    for y, duration, value, width, color in [(745, "10 seconds", "$0.00046", 32, MUTED),
                                           (869, "5 minutes", "$0.01380", 660, INK)]:
        c.text(72, y, 285, 67, duration, 43, bold=True)
        c.text(715, y, 293, 70, value, 47, bold=True)
        c.box(72, y + 72, width, 19, color)
    c.text(72, 1021, 936, 158, "Either bill can dominate. Count the whole job.\nSandbox storage included; paid fees, tax, retries\nand other service charges excluded.", 38)
    c.text(72, 1177, 430, 50, "Replace with your model bill", 28, color=MUTED)
    c.source("E2B pricing", 552, 1177, 360)

    c.page("Five questions worth asking", dark=True)
    c.title("Five questions\nworth asking.")
    questions = [
        "What survives between calls, after a stop\nand on resume? Files, disk, memory.",
        "Does a custom image also reserve a GPU?\nIt doesn't. Request hardware separately.",
        "Where do logs, backups and model calls live?\nMap every data surface and access path.",
        "What happens when a request times out?\nVerify cancellation and recovery.",
        "What's the cost per verified completion?\nKeep credits apart from gross usage.",
    ]
    for i, question in enumerate(questions):
        y = 414 + i * 151
        c.text(72, y, 75, 80, f"0{i + 1}", 40, color=GREEN, bold=True)
        c.text(164, y, 844, 126, question, 40)
    c.text(72, 1171, 936, 50, "Gross campaign cost / verified completed tasks", 32, color=GREEN, bold=True)

    c.page("Why I built and shared the benchmark")
    c.title("A benchmark for\nmy next decision.")
    c.text(72, 417, 936, 211, "File/data checks produced the expected results\nwith E2B, Modal and Google's default code.\nThe tested setups give me a starting shortlist.", 41)
    c.box(72, 662, 936, 385, INK)
    c.text(104, 690, 870, 63, "THE DEEP DIVE", 33, color=GREEN, bold=True)
    c.text(104, 774, 870, 125, "Article: architecture, costs and provider trade-offs.", 43, color=PAPER)
    c.text(104, 909, 870, 120, "Repository: exact setups, workload checks\nand retained results.", 43, color=PAPER)
    for url, y in [(medium_url, 770), (github_url, 900)]:
        if url:
            c.p.insert_link({"kind": fitz.LINK_URI, "from": fitz.Rect(104, y, 976, y + 111), "uri": url})
            c.manifest[-1]["links"].append(url)
            c.transcript.append(f"Resource: {url}\n")
    c.text(72, 1072, 936, 112, "Theo: cheaper capability can enable more work.\nArticle + repository links in the post.", 39)
    c.source("Theo's video", 72, 1180, 460)
    return c


def public_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise argparse.ArgumentTypeError("Use a public HTTPS URL without embedded credentials.")
    if parsed.hostname in {"localhost", "127.0.0.1", "::1"}:
        raise argparse.ArgumentTypeError("Local URLs are not publication destinations.")
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--github-url", type=public_url)
    parser.add_argument("--medium-url", type=public_url)
    args = parser.parse_args()
    carousel = build(args.github_url, args.medium_url)
    carousel.doc.set_metadata({"title": "Cheaper AI. What about the machines?",
                               "subject": "Sandbox news, architecture choices, cost, privacy, features and customization",
                               "keywords": "agent sandboxes, execution, persistence, data residency, economics"})
    output = ROOT / "agent-sandbox-decisions.pdf"
    carousel.doc.save(output, garbage=4, deflate=True)
    (ROOT / "slides.md").write_text("# Cheaper AI. What about the machines?\n\n"
                                   "Readable companion to the nine-page PDF.\n"
                                   + "\n".join(carousel.transcript), encoding="utf-8")
    checks = ROOT / "checks"
    checks.mkdir(exist_ok=True)
    images = []
    with fitz.open(output) as pdf:
        if len(pdf) != 9:
            raise ValueError("Expected nine pages")
        for i, page in enumerate(pdf):
            if abs(page.rect.width / page.rect.height - 0.8) > 0.001:
                raise ValueError("Expected consistent 4:5 pages")
            if not page.get_text().strip():
                raise ValueError(f"Page {i + 1} has no searchable text")
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    for span in line["spans"]:
                        if not page.rect.contains(fitz.Rect(span["bbox"])):
                            raise ValueError(f"Page {i + 1} text outside page")
            pix = page.get_pixmap(matrix=fitz.Matrix(1 / 3, 1 / 3), alpha=False)
            pix.save(checks / f"page-{i + 1:02d}.png")
            images.append(Image.frombytes("RGB", (pix.width, pix.height), pix.samples))
        link_count = sum(len(p.get_links()) for p in pdf)
    sheet = Image.new("RGB", (3 * 384, 3 * 494), "#DBDFD6")
    draw = ImageDraw.Draw(sheet)
    for i, image in enumerate(images):
        x, y = (i % 3) * 384 + 12, (i // 3) * 494 + 12
        sheet.paste(image, (x, y))
        draw.text((x, y + 456), f"PAGE {i + 1}", fill="#172B32")
    sheet.save(checks / "contact-sheet.png")
    validation = {"page_count": 9, "page_size_points": [W, H], "aspect_ratio": "4:5",
                  "selectable_text": True, "text_overflow": False, "text_within_page": True,
                  "link_count": link_count, "bytes": output.stat().st_size,
                  "below_100_mb": output.stat().st_size < 100_000_000,
                  "github_url_supplied": bool(args.github_url), "medium_url_supplied": bool(args.medium_url),
                  "visual_review": "Rendered previews require human/agent inspection; not a layout proof."}
    if not validation["below_100_mb"]:
        raise ValueError("PDF exceeds 100 MB")
    (checks / "validation.json").write_text(json.dumps(validation, indent=2) + "\n")
    (checks / "layout.json").write_text(json.dumps(carousel.manifest, indent=2) + "\n")
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
