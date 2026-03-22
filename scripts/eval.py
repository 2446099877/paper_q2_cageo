from __future__ import annotations

import argparse
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from treatise.config import finalize_config, load_config
from treatise.data.manifests import build_dataloaders
from treatise.engine.evaluator import evaluate_model, persist_evaluation
from treatise.models.rs_scene_model import build_model
from treatise.utils.interpretability import compute_gradcam, save_gradcam_grid
from treatise.utils.repro import ensure_dir, resolve_device, set_seed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate a trained checkpoint.")
    parser.add_argument("--config", required=True, help="Experiment config file.")
    parser.add_argument("--checkpoint", required=True, help="Checkpoint path.")
    parser.add_argument("--seed", type=int, default=None, help="Seed override.")
    parser.add_argument("--split", default="test", choices=["train", "val", "test"])
    parser.add_argument("--gradcam-samples", type=int, default=4)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = finalize_config(load_config(args.config), args.config, seed=args.seed)
    ensure_dir(config["experiment"]["output_dir"])
    set_seed(int(config["experiment"]["seed"]))
    device = resolve_device(config["experiment"].get("device", "cuda"))

    loaders, dataset_info = build_dataloaders(config, seed=int(config["experiment"]["seed"]))
    model = build_model(config["model"], dataset_info["num_classes"]).to(device)

    checkpoint = torch.load(args.checkpoint, map_location=device, weights_only=False)
    model.load_state_dict(checkpoint["model_state_dict"])

    summary, matrix, class_df = evaluate_model(
        model,
        loaders[args.split],
        device=device,
        class_names=dataset_info["class_names"],
        criterion=torch.nn.CrossEntropyLoss(),
        progress=True,
    )
    persist_evaluation(
        summary,
        matrix,
        class_df,
        dataset_info["class_names"],
        config["experiment"]["output_dir"],
        prefix=args.split,
    )

    if args.gradcam_samples > 0:
        images, labels = next(iter(loaders[args.split]))
        images = images[: args.gradcam_samples].to(device)
        labels = labels[: args.gradcam_samples]
        cams, logits = compute_gradcam(model, images)
        predictions = logits.argmax(dim=1).tolist()
        save_gradcam_grid(
            images,
            cams,
            targets=labels.tolist(),
            predictions=predictions,
            class_names=dataset_info["class_names"],
            output_path=Path(config["experiment"]["output_dir"]) / f"{args.split}_gradcam.png",
        )

    print(f"eval finished | split={args.split} | oa={summary['oa']:.4f}")


if __name__ == "__main__":
    main()
