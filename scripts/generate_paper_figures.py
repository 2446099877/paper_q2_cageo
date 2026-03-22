from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from treatise.utils.visuals import plot_metric_bars


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate paper-ready metric summary plots.")
    parser.add_argument("--input", required=True, help="Run root, e.g. outputs/aid_convnext_tiny/mcgf")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_root = Path(args.input)
    csv_path = run_root / "aggregated_metrics.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"{csv_path} not found. Run scripts/aggregate_results.py first."
        )

    detail_df = pd.read_csv(csv_path)
    plot_metric_bars(detail_df, run_root / "paper_metrics.png")
    print(f"saved paper figure to {run_root / 'paper_metrics.png'}")


if __name__ == "__main__":
    main()
