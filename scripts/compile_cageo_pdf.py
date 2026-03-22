from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKET_DIR = ROOT / "paper" / "submission_ready" / "cageo"
TECTONIC = ROOT / "paper" / "springer_template" / "tectonic-bin" / "tectonic.exe"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebuild the C&G packet and compile the Elsevier CAS PDF with the bundled Tectonic binary."
    )
    parser.add_argument(
        "--skip-prepare",
        action="store_true",
        help="Compile the existing packet in place without rebuilding manuscript and packet assets first.",
    )
    return parser.parse_args()


def run_step(command: list[str], cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=str(cwd) if cwd else None, check=True)


def main() -> None:
    args = parse_args()

    if not TECTONIC.exists():
        raise FileNotFoundError(f"Bundled Tectonic binary not found: {TECTONIC}")

    if not args.skip_prepare:
        run_step([sys.executable, str(ROOT / "scripts" / "refresh_paper_assets.py")])
        run_step([sys.executable, str(ROOT / "scripts" / "build_cageo_submission.py")])
        run_step([sys.executable, str(ROOT / "scripts" / "prepare_cageo_packet.py")])

    run_step(
        [
            str(TECTONIC),
            "--keep-logs",
            "--keep-intermediates",
            "manuscript.tex",
        ],
        cwd=PACKET_DIR,
    )

    pdf_path = PACKET_DIR / "manuscript.pdf"
    if not pdf_path.exists():
        raise FileNotFoundError(f"Expected compiled PDF was not created: {pdf_path}")

    print(f"compiled C&G PDF to {pdf_path}")


if __name__ == "__main__":
    main()
