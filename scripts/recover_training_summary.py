from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import torch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from treatise.config import finalize_config, load_config
from treatise.data.manifests import build_dataloaders
from treatise.engine.evaluator import evaluate_model, persist_evaluation
from treatise.models.rs_scene_model import build_model
from treatise.utils.io import save_json
from treatise.utils.repro import ensure_dir, resolve_device, set_seed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Rebuild val/test summaries and summary.json from an existing checkpoint."
    )
    parser.add_argument("--config", required=True, help="Experiment YAML path.")
    parser.add_argument("--checkpoint", required=True, help="Checkpoint path, typically best.pt.")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed override.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = finalize_config(load_config(args.config), args.config, seed=args.seed)
    output_dir = ensure_dir(config["experiment"]["output_dir"])
    set_seed(int(config["experiment"]["seed"]))
    device = resolve_device(config["experiment"].get("device", "cuda"))

    loaders, dataset_info = build_dataloaders(config, seed=int(config["experiment"]["seed"]))
    model = build_model(config["model"], dataset_info["num_classes"]).to(device)

    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])

    criterion = torch.nn.CrossEntropyLoss()
    val_summary, val_matrix, val_df = evaluate_model(
        model,
        loaders["val"],
        device=device,
        class_names=dataset_info["class_names"],
        criterion=criterion,
        progress=True,
    )
    test_summary, test_matrix, test_df = evaluate_model(
        model,
        loaders["test"],
        device=device,
        class_names=dataset_info["class_names"],
        criterion=criterion,
        progress=True,
    )

    persist_evaluation(val_summary, val_matrix, val_df, dataset_info["class_names"], output_dir, prefix="val")
    persist_evaluation(test_summary, test_matrix, test_df, dataset_info["class_names"], output_dir, prefix="test")

    history_path = Path(output_dir) / "history.csv"
    num_epochs_completed = int(len(pd.read_csv(history_path))) if history_path.exists() else int(
        checkpoint.get("epoch", 0)
    )
    best_epoch = int(checkpoint.get("epoch", 0))
    summary = {
        "experiment_name": config["experiment"]["name"],
        "run_name": config["experiment"]["run_name"],
        "seed": int(config["experiment"]["seed"]),
        "output_dir": str(output_dir),
        "best_epoch": best_epoch,
        "history_path": str(history_path),
        "num_epochs_completed": num_epochs_completed,
        "val": val_summary,
        "test": test_summary,
        "class_names": dataset_info["class_names"],
    }
    save_json(summary, Path(output_dir) / "summary.json")
    print(f"recovered summary | seed={summary['seed']} | test_oa={test_summary['oa']:.4f}")


if __name__ == "__main__":
    main()
