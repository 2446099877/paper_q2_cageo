from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Refresh paper tables for the current low-shot route.")
    parser.add_argument(
        "--output-dir",
        default=str(ROOT / "paper" / "generated_lowshot"),
        help="Directory where generated LaTeX tables will be written.",
    )
    return parser.parse_args()


def run_render(command: list[str]) -> None:
    subprocess.run(command, check=True)


def main() -> None:
    args = parse_args()
    script = ROOT / "scripts" / "render_paper_tables.py"
    output_dir = str(Path(args.output_dir).resolve())

    commands = [
        [
            sys.executable,
            str(script),
            "--dataset",
            "AID-low20",
            "--baseline",
            str(ROOT / "outputs" / "aid_low20_convnext_tiny" / "baseline"),
            "--candidate",
            str(ROOT / "outputs" / "aid_low20_dinov2_base" / "adapter_ft1_gcfix"),
            "--candidate-label",
            "DINOv2-B (Adapter, FT)",
            "--variant",
            f"NoCenter={ROOT / 'outputs' / 'aid_low20_dinov2_base' / 'adapter_ft1_nocenter'}",
            "--variant",
            f"NoAdapter={ROOT / 'outputs' / 'aid_low20_dinov2_base' / 'ft1_noadapter'}",
            "--variant",
            f"AdapterOnly={ROOT / 'outputs' / 'aid_low20_dinov2_base' / 'adapter_only'}",
            "--output-dir",
            output_dir,
        ],
        [
            sys.executable,
            str(script),
            "--dataset",
            "NWPU-low20",
            "--baseline",
            str(ROOT / "outputs" / "nwpu_low20_convnext_tiny" / "baseline"),
            "--candidate",
            str(ROOT / "outputs" / "nwpu_low20_dinov2_base" / "adapter_ft1_gcfix"),
            "--candidate-label",
            "DINOv2-B (Adapter, FT)",
            "--variant",
            f"NoCenter={ROOT / 'outputs' / 'nwpu_low20_dinov2_base' / 'adapter_ft1_nocenter'}",
            "--variant",
            f"NoAdapter={ROOT / 'outputs' / 'nwpu_low20_dinov2_base' / 'ft1_noadapter'}",
            "--variant",
            f"AdapterOnly={ROOT / 'outputs' / 'nwpu_low20_dinov2_base' / 'adapter_only'}",
            "--output-dir",
            output_dir,
        ],
    ]

    for command in commands:
        run_render(command)

    print(f"paper assets refreshed under {output_dir}")


if __name__ == "__main__":
    main()
