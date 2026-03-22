from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from treatise.config import dump_yaml, finalize_config, load_config
from treatise.data.manifests import build_dataloaders
from treatise.engine.trainer import fit
from treatise.models.rs_scene_model import build_model
from treatise.utils.io import save_json
from treatise.utils.repro import ensure_dir, resolve_device, set_seed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train a remote sensing scene classifier.")
    parser.add_argument("--config", required=True, help="Path to the experiment YAML file.")
    parser.add_argument("--seed", type=int, default=None, help="Optional seed override.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only build the data loaders and model, then exit.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raw_config = load_config(args.config)
    config = finalize_config(raw_config, args.config, seed=args.seed)

    output_dir = ensure_dir(config["experiment"]["output_dir"])
    dump_yaml(config, output_dir / "resolved_config.yaml")
    set_seed(
        int(config["experiment"]["seed"]),
        deterministic=bool(config["experiment"].get("deterministic", False)),
    )
    device = resolve_device(config["experiment"].get("device", "cuda"))

    loaders, dataset_info = build_dataloaders(config, seed=int(config["experiment"]["seed"]))
    save_json(dataset_info, output_dir / "dataset_info.json")

    model = build_model(config["model"], dataset_info["num_classes"]).to(device)

    if args.dry_run:
        print(
            f"dry-run ok | device={device.type} | classes={dataset_info['num_classes']} | "
            f"splits={dataset_info['split_sizes']}"
        )
        return

    summary = fit(
        model=model,
        loaders=loaders,
        config=config,
        class_names=dataset_info["class_names"],
        device=device,
    )
    print(f"finished | test_oa={summary['test']['oa']:.4f} | output={summary['output_dir']}")


if __name__ == "__main__":
    main()
