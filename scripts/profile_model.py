from __future__ import annotations

import argparse
import sys
from pathlib import Path

import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from treatise.config import finalize_config, load_config
from treatise.data.manifests import KNOWN_NUM_CLASSES
from treatise.models.rs_scene_model import build_model


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Profile parameter count and optional FLOPs.")
    parser.add_argument("--config", required=True, help="Experiment config file.")
    parser.add_argument("--num-classes", type=int, default=None, help="Override class count.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = finalize_config(load_config(args.config), args.config)
    dataset_name = config["data"]["dataset_name"]
    num_classes = args.num_classes or KNOWN_NUM_CLASSES.get(dataset_name, 30)
    model = build_model(config["model"], num_classes=num_classes)

    params = sum(parameter.numel() for parameter in model.parameters())
    trainable = sum(parameter.numel() for parameter in model.parameters() if parameter.requires_grad)
    print(f"params={params:,}")
    print(f"trainable_params={trainable:,}")

    dummy = torch.randn(1, 3, int(config["data"]["image_size"]), int(config["data"]["image_size"]))
    try:
        from thop import profile

        macs, _ = profile(model, inputs=(dummy,), verbose=False)
        flops = macs * 2
        print(f"approx_flops={int(flops):,}")
    except Exception as exc:
        print(f"flops=unavailable ({exc})")


if __name__ == "__main__":
    main()
