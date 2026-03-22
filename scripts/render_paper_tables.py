from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from treatise.utils.io import load_json


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render LaTeX tables for the paper from experiment outputs.")
    parser.add_argument("--dataset", required=True, help="Display name used in the paper.")
    parser.add_argument("--baseline", required=True, help="Run root for baseline.")
    parser.add_argument("--candidate", required=True, help="Run root for full proposed method.")
    parser.add_argument(
        "--baseline-label",
        default="ConvNeXt-Tiny",
        help="Display name used for the baseline method.",
    )
    parser.add_argument(
        "--candidate-label",
        default="Proposed",
        help="Display name used for the proposed method.",
    )
    parser.add_argument(
        "--variant",
        action="append",
        default=[],
        help="Optional ablation row in the form 'Label=run_root'. Can be passed multiple times.",
    )
    parser.add_argument("--msca", default=None, help="Backward-compatible alias for an optional ablation.")
    parser.add_argument("--lgfh", default=None, help="Backward-compatible alias for an optional ablation.")
    parser.add_argument(
        "--output-dir",
        default="paper/generated",
        help="Directory where LaTeX fragments will be written.",
    )
    return parser.parse_args()


def _load_run_summary(run_root: Path) -> dict:
    aggregated_path = run_root / "aggregated_summary.csv"
    detail_path = run_root / "aggregated_metrics.csv"
    if aggregated_path.exists():
        agg = pd.read_csv(aggregated_path).iloc[0]
        num_runs = len(pd.read_csv(detail_path)) if detail_path.exists() else 1
        return {
            "oa": float(agg["oa_mean"]),
            "oa_std": float(agg.get("oa_std", 0.0)),
            "aa": float(agg["aa_mean"]),
            "aa_std": float(agg.get("aa_std", 0.0)),
            "kappa": float(agg["kappa_mean"]),
            "kappa_std": float(agg.get("kappa_std", 0.0)),
            "num_runs": int(num_runs),
        }

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

    seed_summaries = sorted(run_root.glob("seed_*/summary.json"))
    if not seed_summaries:
        raise FileNotFoundError(f"No summary files found under {run_root}")

    frame = pd.DataFrame(
        [
            load_json(summary_path)["test"]
            for summary_path in seed_summaries
        ]
    )
    return {
        "oa": float(frame["oa"].mean()),
        "oa_std": float(frame["oa"].std(ddof=0)),
        "aa": float(frame["aa"].mean()),
        "aa_std": float(frame["aa"].std(ddof=0)),
        "kappa": float(frame["kappa"].mean()),
        "kappa_std": float(frame["kappa"].std(ddof=0)),
        "num_runs": int(len(frame)),
    }


def _load_seedwise_oa(run_root: Path) -> dict[int, float]:
    detail_path = run_root / "aggregated_metrics.csv"
    if detail_path.exists():
        frame = pd.read_csv(detail_path)
        return {
            int(row["seed"]): float(row["oa"])
            for _, row in frame.iterrows()
        }

    summary_json = run_root / "summary.json"
    if summary_json.exists():
        payload = load_json(summary_json)
        seed = payload.get("seed")
        if seed is None:
            return {}
        return {int(seed): float(payload["test"]["oa"])}

    seedwise: dict[int, float] = {}
    for summary_path in sorted(run_root.glob("seed_*/summary.json")):
        payload = load_json(summary_path)
        seedwise[int(payload["seed"])] = float(payload["test"]["oa"])
    return seedwise


def _fmt(summary: dict, metric: str) -> str:
    mean = summary[metric]
    std = summary[f"{metric}_std"]
    if summary["num_runs"] <= 1:
        return f"{mean:.4f}"
    return f"{mean:.4f} $\\pm$ {std:.4f}"


def _format_method_label(label: str) -> str:
    mapping = {
        "DINOv2-Base+Adapter+FT": "DINOv2-B (Adapter, FT)",
        "DINOv2-Base+NoAdapter+FT": "DINOv2-B (NoAdapter, FT)",
        "AdapterOnly": "Adapter only",
    }
    if label in mapping:
        return mapping[label]
    return label.replace("DINOv2-Base", "DINOv2-B").replace("+", " + ")


def _parse_variants(args: argparse.Namespace) -> list[tuple[str, dict, Path]]:
    variants: list[tuple[str, dict, Path]] = []
    if args.msca:
        run_root = Path(args.msca).resolve()
        variants.append(("+ MSCA", _load_run_summary(run_root), run_root))
    if args.lgfh:
        run_root = Path(args.lgfh).resolve()
        variants.append(("+ LGFH", _load_run_summary(run_root), run_root))

    for raw_item in args.variant:
        if "=" not in raw_item:
            raise ValueError(
                f"Invalid --variant value: {raw_item!r}. Expected 'Label=run_root'."
            )
        label, run_root = raw_item.split("=", 1)
        label = label.strip()
        run_root = run_root.strip()
        if not label or not run_root:
            raise ValueError(
                f"Invalid --variant value: {raw_item!r}. Expected 'Label=run_root'."
            )
        run_root_path = Path(run_root).resolve()
        variants.append((label, _load_run_summary(run_root_path), run_root_path))
    return variants


def render_main_results(
    dataset: str,
    baseline_label: str,
    candidate_label: str,
    baseline: dict,
    candidate: dict,
) -> str:
    lines = [
        "\\begin{table}[t]",
        "  \\centering",
        f"  \\caption{{Main results on {dataset}.}}",
        f"  \\label{{tab:{dataset.lower().replace(' ', '_')}_main}}",
        "  \\begin{tabular}{l c c c c}",
        "    \\toprule",
        "    Method & OA & AA & Kappa & $\\Delta$OA \\\\",
        "    \\midrule",
        f"    {baseline_label} & {_fmt(baseline, 'oa')} & {_fmt(baseline, 'aa')} & {_fmt(baseline, 'kappa')} & -- \\\\",
        f"    {candidate_label} & {_fmt(candidate, 'oa')} & {_fmt(candidate, 'aa')} & {_fmt(candidate, 'kappa')} & {candidate['oa'] - baseline['oa']:+.4f} \\\\",
        "    \\bottomrule",
        "  \\end{tabular}",
        "\\end{table}",
        "",
    ]
    return "\n".join(lines)


def render_ablation(
    dataset: str,
    baseline_label: str,
    candidate_label: str,
    baseline: dict,
    variants: list[tuple[str, dict]],
    candidate: dict,
) -> str:
    rows = [(baseline_label, baseline), *variants, (candidate_label, candidate)]
    lines = [
        "\\begin{table}[t]",
        "  \\centering",
        f"  \\caption{{Three-seed mean$\\pm$std ablation results on {dataset} under the fixed split protocol.}}",
        f"  \\label{{tab:{dataset.lower().replace(' ', '_')}_ablation}}",
        "  \\begin{tabular}{l c c c}",
        "    \\toprule",
        "    Variant & OA & AA & Kappa \\\\",
        "    \\midrule",
    ]
    for label, summary in rows:
        label_tex = _format_method_label(label)
        if summary is None:
            lines.append(f"    {label_tex} & TBD & TBD & TBD \\\\")
        else:
            lines.append(
                f"    {label_tex} & {_fmt(summary, 'oa')} & {_fmt(summary, 'aa')} & {_fmt(summary, 'kappa')} \\\\"
            )
    lines.extend(["    \\bottomrule", "  \\end{tabular}", "\\end{table}", ""])
    return "\n".join(lines)


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    baseline = _load_run_summary(Path(args.baseline).resolve())
    candidate = _load_run_summary(Path(args.candidate).resolve())
    variants = _parse_variants(args)

    dataset_key = args.dataset.lower().replace(" ", "_")
    main_text = render_main_results(
        args.dataset,
        args.baseline_label,
        args.candidate_label,
        baseline,
        candidate,
    )
    ablation_text = render_ablation(
        args.dataset,
        args.baseline_label,
        args.candidate_label,
        baseline,
        [(label, summary) for label, summary, _ in variants],
        candidate,
    )

    (output_dir / f"{dataset_key}_main_results.tex").write_text(main_text, encoding="utf-8")
    (output_dir / f"{dataset_key}_ablation.tex").write_text(ablation_text, encoding="utf-8")
    payload = {
        "dataset": args.dataset,
        "dataset_key": dataset_key,
        "baseline_label": args.baseline_label,
        "candidate_label": args.candidate_label,
        "baseline": baseline,
        "baseline_seedwise_oa": _load_seedwise_oa(Path(args.baseline).resolve()),
        "candidate": candidate,
        "candidate_seedwise_oa": _load_seedwise_oa(Path(args.candidate).resolve()),
        "variants": [
            {
                "label": label,
                "summary": summary,
                "seedwise_oa": _load_seedwise_oa(run_root),
            }
            for label, summary, run_root in variants
        ],
    }
    (output_dir / f"{dataset_key}_payload.json").write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    render_project_tables(output_dir)
    print(f"rendered tables under {output_dir}")


def render_project_tables(output_dir: Path) -> None:
    payload_paths = sorted(output_dir.glob("*_payload.json"))
    if not payload_paths:
        return

    payloads = [
        json.loads(payload_path.read_text(encoding="utf-8"))
        for payload_path in payload_paths
    ]

    main_lines = [
        "\\begin{table}[t]",
        "  \\centering",
        "  \\scriptsize",
        "  \\setlength{\\tabcolsep}{2pt}",
        "  \\caption{Three-seed mean$\\pm$std results under the fixed 20-training and 10-validation images-per-class protocol. $\\Delta$OA is measured against the ConvNeXt-Tiny baseline on the same split manifests.}",
        "  \\label{tab:main_results}",
        "  \\begin{tabular}{l >{\\raggedright\\arraybackslash}p{0.22\\textwidth} c c c c}",
        "    \\toprule",
        "    Dataset & Method & OA & AA & Kappa & $\\Delta$OA \\\\",
        "    \\midrule",
    ]
    for payload in payloads:
        dataset = payload["dataset"].split("-")[0]
        baseline_label = payload.get("baseline_label", "Baseline")
        candidate_label = payload.get("candidate_label", "Proposed")
        baseline_label_tex = _format_method_label(baseline_label)
        candidate_label_tex = _format_method_label(candidate_label)
        baseline = payload["baseline"]
        candidate = payload["candidate"]
        main_lines.append(
            f"    {dataset} & {baseline_label_tex} & {_fmt(baseline, 'oa')} & {_fmt(baseline, 'aa')} & {_fmt(baseline, 'kappa')} & -- \\\\"
        )
        main_lines.append(
            f"    {dataset} & {candidate_label_tex} & {_fmt(candidate, 'oa')} & {_fmt(candidate, 'aa')} & {_fmt(candidate, 'kappa')} & {candidate['oa'] - baseline['oa']:+.4f} \\\\"
        )
    main_lines.extend(["    \\bottomrule", "  \\end{tabular}", "\\end{table}", ""])
    (output_dir / "main_results.tex").write_text("\n".join(main_lines), encoding="utf-8")

    ablation_blocks = []
    for payload in payloads:
        ablation_blocks.append(
            render_ablation(
                payload["dataset"],
                payload.get("baseline_label", "Baseline"),
                payload.get("candidate_label", "Proposed"),
                payload["baseline"],
                [
                    (item["label"], item["summary"])
                    for item in payload.get("variants", [])
                ],
                payload["candidate"],
            )
        )
    (output_dir / "ablation_results.tex").write_text(
        "\n".join(ablation_blocks),
        encoding="utf-8",
    )

    stability_lines = [
        "\\begin{table}[t]",
        "  \\centering",
        "  \\scriptsize",
        "  \\setlength{\\tabcolsep}{3pt}",
        "  \\caption{OA mean and standard deviation of the full method and the key same-backbone controls. NoAdapter isolates the role of the residual adapter, and NoCenter isolates the contribution of feature-center regularization.}",
        "  \\label{tab:stability_results}",
        "  \\begin{tabular}{l >{\\raggedright\\arraybackslash}p{0.22\\textwidth} c c c}",
        "    \\toprule",
        "    Dataset & Variant & OA Mean & OA Std & $\\Delta$OA vs Full \\\\",
        "    \\midrule",
    ]
    for payload in payloads:
        full = payload["candidate"]
        full_label = "Full setting"
        full_std = float(full["oa_std"])
        variant_map = {item["label"]: item["summary"] for item in payload.get("variants", [])}
        for label in ("NoAdapter", "NoCenter"):
            summary = variant_map.get(label)
            if summary is None:
                continue
            delta = float(summary["oa"]) - float(full["oa"])
            stability_lines.append(
                f"    {payload['dataset'].split('-')[0]} & {label} & {float(summary['oa']):.4f} & {float(summary['oa_std']):.4f} & {delta:+.4f} \\\\"
            )
        stability_lines.append(
            f"    {payload['dataset'].split('-')[0]} & {full_label} & {float(full['oa']):.4f} & {full_std:.4f} & +0.0000 \\\\"
        )
    stability_lines.extend(["    \\bottomrule", "  \\end{tabular}", "\\end{table}", ""])
    (output_dir / "stability_results.tex").write_text(
        "\n".join(stability_lines),
        encoding="utf-8",
    )

    target_variant_labels = {"NoAdapter", "NoCenter"}
    seeds = [3407, 3408, 3409]
    seedwise_lines = [
        "\\begin{table}[t]",
        "  \\centering",
        "  \\caption{Per-seed OA values on the fixed split manifests used by all compared methods.}",
        "  \\label{tab:seedwise_results}",
        "  \\begin{tabular}{l l c c c}",
        "    \\toprule",
        "    Dataset & Variant & Seed 3407 & Seed 3408 & Seed 3409 \\\\",
        "    \\midrule",
    ]
    for payload in payloads:
        rows = [
            (_format_method_label(payload["baseline_label"]), payload.get("baseline_seedwise_oa", {})),
            (_format_method_label(payload["candidate_label"]), payload.get("candidate_seedwise_oa", {})),
        ]
        rows.extend(
            (
                _format_method_label(item["label"]),
                item.get("seedwise_oa", {}),
            )
            for item in payload.get("variants", [])
            if item["label"] in target_variant_labels
        )
        for label, seedwise in rows:
            entries = []
            for seed in seeds:
                value = seedwise.get(str(seed), seedwise.get(seed))
                entries.append("--" if value is None else f"{float(value):.4f}")
            seedwise_lines.append(
                f"    {payload['dataset']} & {label} & {entries[0]} & {entries[1]} & {entries[2]} \\\\"
            )
    seedwise_lines.extend(["    \\bottomrule", "  \\end{tabular}", "\\end{table}", ""])
    (output_dir / "seedwise_results.tex").write_text(
        "\n".join(seedwise_lines),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
