from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIR = ROOT / "paper" / "submission_ready" / "cageo"


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
