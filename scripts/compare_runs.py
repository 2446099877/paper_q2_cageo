from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from treatise.utils.io import load_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare baseline and proposed experiment outputs.")
    parser.add_argument("--baseline", required=True, help="Baseline run root.")
    parser.add_argument("--candidate", required=True, help="Candidate run root.")
    parser.add_argument("--baseline-label", default="ConvNeXt-Tiny", help="Baseline display name.")
    parser.add_argument("--candidate-label", default="Candidate", help="Candidate display name.")
    parser.add_argument("--dataset", default=None, help="Optional dataset display name.")
    return parser.parse_args()


def _load_run_summary(run_root: Path) -> dict:
    aggregated_path = run_root / "aggregated_summary.csv"
    detail_path = run_root / "aggregated_metrics.csv"
    if aggregated_path.exists():
        summary = pd.read_csv(aggregated_path).iloc[0].to_dict()
        if detail_path.exists():
            detail = pd.read_csv(detail_path)
            summary["num_runs"] = int(len(detail))
        else:
            summary["num_runs"] = 1
        return {
            "oa": float(summary["oa_mean"]),
            "oa_std": float(summary.get("oa_std", 0.0)),
            "aa": float(summary["aa_mean"]),
            "aa_std": float(summary.get("aa_std", 0.0)),
            "kappa": float(summary["kappa_mean"]),
            "kappa_std": float(summary.get("kappa_std", 0.0)),
            "num_runs": int(summary["num_runs"]),
        }

    seed_summaries = sorted(run_root.glob("seed_*/summary.json"))
    if not seed_summaries:
        summary_json = run_root / "summary.json"
        if summary_json.exists():
            payload = load_json(summary_json)
            return {
                "oa": float(payload["test"]["oa"]),
                "oa_std": 0.0,
                "aa": float(payload["test"]["aa"]),
                "aa_std": 0.0,
                "kappa": float(payload["test"]["kappa"]),
                "kappa_std": 0.0,
                "num_runs": 1,
            }
        raise FileNotFoundError(f"No summary files found under {run_root}")

    rows = []
    for summary_path in seed_summaries:
        payload = load_json(summary_path)
        rows.append(
            {
                "oa": payload["test"]["oa"],
                "aa": payload["test"]["aa"],
                "kappa": payload["test"]["kappa"],
            }
        )

    frame = pd.DataFrame(rows)
    return {
        "oa": float(frame["oa"].mean()),
        "oa_std": float(frame["oa"].std(ddof=0)),
        "aa": float(frame["aa"].mean()),
        "aa_std": float(frame["aa"].std(ddof=0)),
        "kappa": float(frame["kappa"].mean()),
        "kappa_std": float(frame["kappa"].std(ddof=0)),
        "num_runs": int(len(frame)),
    }


def _format_pm(mean: float, std: float, num_runs: int) -> str:
    if num_runs <= 1:
        return f"{mean:.4f}"
    return f"{mean:.4f} ± {std:.4f}"


def build_comparison_table(
    dataset_name: str,
    baseline_label: str,
    candidate_label: str,
    baseline: dict,
    candidate: dict,
) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "dataset": dataset_name,
                "method": baseline_label,
                "oa": _format_pm(baseline["oa"], baseline["oa_std"], baseline["num_runs"]),
                "aa": _format_pm(baseline["aa"], baseline["aa_std"], baseline["num_runs"]),
                "kappa": _format_pm(baseline["kappa"], baseline["kappa_std"], baseline["num_runs"]),
                "delta_oa": "",
                "delta_aa": "",
                "delta_kappa": "",
            },
            {
                "dataset": dataset_name,
                "method": candidate_label,
                "oa": _format_pm(candidate["oa"], candidate["oa_std"], candidate["num_runs"]),
                "aa": _format_pm(candidate["aa"], candidate["aa_std"], candidate["num_runs"]),
                "kappa": _format_pm(candidate["kappa"], candidate["kappa_std"], candidate["num_runs"]),
                "delta_oa": f"{candidate['oa'] - baseline['oa']:+.4f}",
                "delta_aa": f"{candidate['aa'] - baseline['aa']:+.4f}",
                "delta_kappa": f"{candidate['kappa'] - baseline['kappa']:+.4f}",
            },
        ]
    )


def write_outputs(output_dir: Path, table: pd.DataFrame) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    table.to_csv(output_dir / "comparison_table.csv", index=False)
    (output_dir / "comparison_table.md").write_text(table.to_markdown(index=False), encoding="utf-8")

    latex_lines = [
        "\\begin{tabular}{l l c c c c c c}",
        "\\toprule",
        "Dataset & Method & OA & AA & Kappa & $\\Delta$OA & $\\Delta$AA & $\\Delta\\kappa$ \\\\",
        "\\midrule",
    ]
    for _, row in table.iterrows():
        latex_lines.append(
            f"{row['dataset']} & {row['method']} & {row['oa']} & {row['aa']} & {row['kappa']} & "
            f"{row['delta_oa']} & {row['delta_aa']} & {row['delta_kappa']} \\\\"
        )
    latex_lines.extend(["\\bottomrule", "\\end{tabular}", ""])
    (output_dir / "comparison_table.tex").write_text("\n".join(latex_lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    baseline_root = Path(args.baseline).resolve()
    candidate_root = Path(args.candidate).resolve()
    dataset_name = args.dataset or candidate_root.parent.name

    baseline = _load_run_summary(baseline_root)
    candidate = _load_run_summary(candidate_root)
    table = build_comparison_table(
        dataset_name=dataset_name,
        baseline_label=args.baseline_label,
        candidate_label=args.candidate_label,
        baseline=baseline,
        candidate=candidate,
    )

    output_dir = candidate_root / "comparison_vs_baseline"
    write_outputs(output_dir, table)
    print(f"comparison saved to {output_dir}")


if __name__ == "__main__":
    main()
