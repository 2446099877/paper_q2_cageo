from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from treatise.utils.io import load_json
from treatise.utils.visuals import plot_metric_bars


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Aggregate seed-wise experiment summaries.")
    parser.add_argument("--input", required=True, help="Run root, e.g. outputs/aid_convnext_tiny/mcgf")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_root = Path(args.input)
    summaries = sorted(run_root.glob("seed_*/summary.json"))
    if not summaries:
        raise FileNotFoundError(f"No summary.json files found under {run_root}")

    rows = []
    for summary_path in summaries:
        payload = load_json(summary_path)
        rows.append(
            {
                "run": summary_path.parent.name,
                "seed": payload["seed"],
                "oa": payload["test"]["oa"],
                "aa": payload["test"]["aa"],
                "kappa": payload["test"]["kappa"],
                "best_epoch": payload["best_epoch"],
            }
        )

    detail_df = pd.DataFrame(rows).sort_values("seed")
    detail_df.to_csv(run_root / "aggregated_metrics.csv", index=False)

    summary_df = pd.DataFrame(
        [
            {
                "oa_mean": detail_df["oa"].mean(),
                "oa_std": detail_df["oa"].std(ddof=0),
                "aa_mean": detail_df["aa"].mean(),
                "aa_std": detail_df["aa"].std(ddof=0),
                "kappa_mean": detail_df["kappa"].mean(),
                "kappa_std": detail_df["kappa"].std(ddof=0),
                "best_epoch_mean": detail_df["best_epoch"].mean(),
            }
        ]
    )
    summary_df.to_csv(run_root / "aggregated_summary.csv", index=False)

    markdown = detail_df.to_markdown(index=False)
    (run_root / "aggregated_metrics.md").write_text(markdown, encoding="utf-8")
    plot_metric_bars(detail_df, run_root / "aggregated_metrics.png")
    print(f"aggregated {len(detail_df)} runs under {run_root}")


if __name__ == "__main__":
    main()
