from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from treatise.data.manifests import KNOWN_NUM_CLASSES


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate dataset folder structure and summarize counts.")
    parser.add_argument("--root", required=True, help="Dataset root folder.")
    parser.add_argument("--name", required=True, help="Dataset name, e.g. AID or UCMerced.")
    parser.add_argument(
        "--extensions",
        nargs="+",
        default=[".jpg", ".jpeg", ".png", ".tif", ".tiff"],
        help="Allowed image extensions.",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional output directory for csv/markdown reports.",
    )
    return parser.parse_args()


def inspect_dataset(root: Path, extensions: set[str]) -> tuple[pd.DataFrame, dict]:
    if not root.exists():
        raise FileNotFoundError(f"Dataset root not found: {root}")

    class_dirs = sorted(path for path in root.iterdir() if path.is_dir())
    if not class_dirs:
        raise FileNotFoundError(f"No class folders found under {root}")

    rows = []
    total_images = 0
    for class_dir in class_dirs:
        image_files = sorted(
            path
            for path in class_dir.rglob("*")
            if path.is_file() and path.suffix.lower() in extensions
        )
        total_images += len(image_files)
        rows.append(
            {
                "class_name": class_dir.name,
                "num_images": len(image_files),
                "sample_path": (
                    str(image_files[0].relative_to(root)).replace("\\", "/")
                    if image_files
                    else ""
                ),
            }
        )

    summary_df = pd.DataFrame(rows).sort_values(["num_images", "class_name"], ascending=[True, True])
    metadata = {
        "num_classes": len(summary_df),
        "total_images": int(total_images),
        "min_images_per_class": int(summary_df["num_images"].min()),
        "max_images_per_class": int(summary_df["num_images"].max()),
        "mean_images_per_class": float(summary_df["num_images"].mean()),
        "empty_classes": summary_df.loc[summary_df["num_images"] == 0, "class_name"].tolist(),
    }
    return summary_df, metadata


def write_report(
    dataset_name: str,
    root: Path,
    class_df: pd.DataFrame,
    metadata: dict,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / f"{dataset_name.lower()}_dataset_summary.csv"
    md_path = output_dir / f"{dataset_name.lower()}_dataset_summary.md"

    class_df.to_csv(csv_path, index=False)

    lines = [
        f"# Dataset Report: {dataset_name}",
        "",
        f"- Root: `{root}`",
        f"- Classes: `{metadata['num_classes']}`",
        f"- Images: `{metadata['total_images']}`",
        f"- Min images per class: `{metadata['min_images_per_class']}`",
        f"- Max images per class: `{metadata['max_images_per_class']}`",
        f"- Mean images per class: `{metadata['mean_images_per_class']:.2f}`",
    ]
    if metadata["empty_classes"]:
        lines.append(f"- Empty classes: `{', '.join(metadata['empty_classes'])}`")
    else:
        lines.append("- Empty classes: `None`")

    lines.extend(
        [
            "",
            "## Per-class counts",
            "",
            class_df.to_markdown(index=False),
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    root = Path(args.root).resolve()
    dataset_name = args.name
    expected_classes = KNOWN_NUM_CLASSES.get(dataset_name)
    class_df, metadata = inspect_dataset(root, {extension.lower() for extension in args.extensions})

    print(f"dataset={dataset_name}")
    print(f"root={root}")
    print(f"classes={metadata['num_classes']}")
    print(f"images={metadata['total_images']}")
    print(f"min_per_class={metadata['min_images_per_class']}")
    print(f"max_per_class={metadata['max_images_per_class']}")
    print(f"mean_per_class={metadata['mean_images_per_class']:.2f}")

    if expected_classes is not None:
        if metadata["num_classes"] == expected_classes:
            print(f"class_check=ok ({expected_classes})")
        else:
            print(f"class_check=warning expected {expected_classes} but found {metadata['num_classes']}")

    if metadata["empty_classes"]:
        print(f"empty_classes={metadata['empty_classes']}")

    if args.output:
        output_dir = Path(args.output).resolve()
        write_report(dataset_name, root, class_df, metadata, output_dir)
        print(f"report_dir={output_dir}")


if __name__ == "__main__":
    main()
