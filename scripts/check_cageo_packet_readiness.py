from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIR = ROOT / "paper" / "submission_ready" / "cageo"
HIGHLIGHTS_DRAFT = ROOT / "docs" / "submission_packets" / "cageo_highlights_draft.md"
HIGHLIGHT_LIMIT = 85


CHECKS = [
    (
        "Author 1 placeholder",
        PACKET_DIR / "manuscript.tex",
        r"\author[1]{Author 1}",
    ),
    (
        "Author 2 placeholder",
        PACKET_DIR / "manuscript.tex",
        r"\author[1]{Author 2}",
    ),
    (
        "Author affiliation placeholder",
        PACKET_DIR / "manuscript.tex",
        r"\address[1]{Author affiliation}",
    ),
    (
        "Author signature placeholder",
        PACKET_DIR / "manuscript.tex",
        r"Authors",
    ),
    (
        "Corresponding author placeholder in code availability",
        PACKET_DIR / "manuscript.tex",
        r"corresponding author information to be inserted before submission",
    ),
    (
        "Program size placeholder",
        PACKET_DIR / "manuscript.tex",
        r"repository details to be finalized before submission",
    ),
    (
        "Repository placeholder",
        PACKET_DIR / "manuscript.tex",
        r"will be released in a public repository upon acceptance",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check whether the local C&G submission packet still contains required placeholders."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any placeholder is still present.",
    )
    return parser.parse_args()


def normalize_text(text: str) -> str:
    return " ".join(text.split())


def extract_draft_highlights(path: Path) -> list[str]:
    highlights: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            highlights.append(normalize_text(stripped[2:]))
    return highlights


def extract_manuscript_highlights(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    match = re.search(
        r"\\begin\{highlights\}(.*?)\\end\{highlights\}",
        text,
        flags=re.S,
    )
    if not match:
        return []
    block = match.group(1)
    return [
        normalize_text(item)
        for item in re.findall(r"\\item\s+([^\n]+)", block)
    ]


def main() -> None:
    args = parse_args()
    missing_items: list[str] = []

    pdf_path = PACKET_DIR / "manuscript.pdf"
    print(f"packet_dir: {PACKET_DIR}")
    print(f"pdf_exists: {'yes' if pdf_path.exists() else 'no'}")

    for label, path, token in CHECKS:
        if not path.exists():
            missing_items.append(f"{label}: file missing -> {path}")
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if token in text:
            missing_items.append(f"{label}: {path}")

    if not HIGHLIGHTS_DRAFT.exists():
        missing_items.append(f"Highlights draft missing: {HIGHLIGHTS_DRAFT}")
    else:
        draft_highlights = extract_draft_highlights(HIGHLIGHTS_DRAFT)
        if not 3 <= len(draft_highlights) <= 5:
            missing_items.append(
                f"Highlights draft must contain 3 to 5 bullets: {HIGHLIGHTS_DRAFT}"
            )
        for index, item in enumerate(draft_highlights, start=1):
            if len(item) > HIGHLIGHT_LIMIT:
                missing_items.append(
                    f"Highlights draft line {index} exceeds {HIGHLIGHT_LIMIT} chars ({len(item)}): {HIGHLIGHTS_DRAFT}"
                )

        manuscript_path = PACKET_DIR / "manuscript.tex"
        if manuscript_path.exists():
            manuscript_highlights = extract_manuscript_highlights(manuscript_path)
            if manuscript_highlights != draft_highlights:
                missing_items.append(
                    f"Highlights mismatch between draft and manuscript: {manuscript_path}"
                )
        else:
            missing_items.append(f"Generated manuscript missing: {manuscript_path}")

    if missing_items:
        print("outstanding_placeholders:")
        for item in missing_items:
            print(f"- {item}")
        if args.strict:
            sys.exit(1)
    else:
        print("outstanding_placeholders: none")


if __name__ == "__main__":
    main()
