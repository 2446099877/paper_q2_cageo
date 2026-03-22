from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from treatise.config import load_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one experiment over multiple seeds.")
    parser.add_argument("--config", required=True, help="Experiment config file.")
    parser.add_argument(
        "--seeds",
        type=int,
        nargs="+",
        default=None,
        help="Optional explicit seed list. Defaults to config seeds or [3407, 3408, 3409].",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config(args.config)
    seeds = args.seeds or config.get("experiment", {}).get("seeds", [3407, 3408, 3409])

    script_path = ROOT / "scripts" / "train.py"
    for seed in seeds:
        command = [
            sys.executable,
            str(script_path),
            "--config",
            str(Path(args.config).resolve()),
            "--seed",
            str(seed),
        ]
        subprocess.run(command, check=True)

    print(f"multiseed finished | config={args.config} | seeds={seeds}")


if __name__ == "__main__":
    main()
