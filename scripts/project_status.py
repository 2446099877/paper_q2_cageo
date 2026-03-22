from __future__ import annotations

import argparse
import json
from pathlib import Path


PROJECT_EXPERIMENTS = {
    "AID": {
        "experiment_name": "aid_convnext_tiny",
        "runs": ["baseline", "msca", "lgfh", "mcgf"],
    },
    "UCMerced": {
        "experiment_name": "ucm_convnext_tiny",
        "runs": ["baseline", "msca", "lgfh", "mcgf"],
    },
    "NWPU_RESISC45": {
        "experiment_name": "nwpu_convnext_tiny",
        "runs": ["baseline", "mcgf"],
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Show current experiment/project completion status.")
    parser.add_argument(
        "--root",
        default=".",
        help="Project root. Defaults to current working directory.",
    )
    return parser.parse_args()


def run_status(run_root: Path) -> dict:
    summary_json = run_root / "summary.json"
    agg_csv = run_root / "aggregated_summary.csv"
    comparison_dir = run_root / "comparison_vs_baseline"

    if agg_csv.exists():
        return {
            "status": "aggregated",
            "summary_file": str(agg_csv),
            "comparison_ready": comparison_dir.exists(),
        }
    if summary_json.exists():
        return {
            "status": "single_run",
            "summary_file": str(summary_json),
            "comparison_ready": comparison_dir.exists(),
        }

    seed_runs = sorted(run_root.glob("seed_*/summary.json"))
    if seed_runs:
        return {
            "status": f"{len(seed_runs)}_seed_runs",
            "summary_file": str(seed_runs[0]),
            "comparison_ready": comparison_dir.exists(),
        }

    return {
        "status": "missing",
        "summary_file": "",
        "comparison_ready": False,
    }


def paper_status(project_root: Path) -> dict:
    generated_dir = project_root / "paper" / "generated"
    files = sorted(path.name for path in generated_dir.glob("*.tex"))
    return {
        "generated_tables": files,
        "paper_ready": bool(files),
    }


def dataset_status(project_root: Path) -> dict:
    data_root = project_root / "data" / "raw"
    status = {}
    for name in ["AID", "UCMerced", "NWPU_RESISC45"]:
        path = data_root / name
        status[name] = {
            "exists": path.exists(),
            "path": str(path),
        }
    return status


def build_status(project_root: Path) -> dict:
    payload = {
        "datasets": dataset_status(project_root),
        "experiments": {},
        "paper": paper_status(project_root),
    }
    for dataset, entry in PROJECT_EXPERIMENTS.items():
        experiment_root = project_root / "outputs" / entry["experiment_name"]
        payload["experiments"][dataset] = {}
        for run_name in entry["runs"]:
            payload["experiments"][dataset][run_name] = run_status(experiment_root / run_name)
    return payload


def main() -> None:
    args = parse_args()
    project_root = Path(args.root).resolve()
    payload = build_status(project_root)
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
