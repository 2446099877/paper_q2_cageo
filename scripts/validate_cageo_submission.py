from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_step(command: list[str]) -> None:
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    run_step([sys.executable, str(ROOT / "scripts" / "compile_cageo_pdf.py")])
    run_step([sys.executable, str(ROOT / "scripts" / "check_cageo_packet_readiness.py")])
    run_step([sys.executable, "-m", "unittest", "discover", "-s", "tests"])
    print("validated C&G submission packet successfully")


if __name__ == "__main__":
    main()
