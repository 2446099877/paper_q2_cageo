from __future__ import annotations

import random
from pathlib import Path
from typing import Iterable

import pandas as pd
from PIL import Image
from torch.utils.data import DataLoader, Dataset

from .transforms import build_eval_transform, build_train_transform


KNOWN_NUM_CLASSES = {
    "AID": 30,
    "UCMerced": 21,
    "NWPU_RESISC45": 45,
}


def _iter_images(class_dir: Path, extensions: set[str]) -> list[Path]:
    return sorted(
        path
        for path in class_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in extensions
    )


def create_manifest(
    root: str | Path,
    output_path: str | Path,
    protocol_train_ratio: float,
    val_ratio_from_train: float,
    seed: int,
    extensions: Iterable[str],
    train_shots_per_class: int | None = None,
    val_shots_per_class: int | None = None,
) -> Path:
    root = Path(root)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    extension_set = {extension.lower() for extension in extensions}

    class_dirs = sorted(path for path in root.iterdir() if path.is_dir())
    if not class_dirs:
        raise FileNotFoundError(f"No class folders found under {root}")

    rng = random.Random(seed)
    rows: list[dict] = []
    for class_index, class_dir in enumerate(class_dirs):
        images = _iter_images(class_dir, extension_set)
        if len(images) < 3:
            raise ValueError(f"Class {class_dir.name} has too few images: {len(images)}")

        rng.shuffle(images)
        if train_shots_per_class is not None:
            train_size = int(train_shots_per_class)
            if train_size < 1:
                raise ValueError("train_shots_per_class must be at least 1.")

            requested_val = val_shots_per_class
            if requested_val is None:
                requested_val = max(1, int(round(train_size * val_ratio_from_train)))
            val_size = int(requested_val)

            if val_size < 1:
                raise ValueError("val_shots_per_class must be at least 1.")
            if train_size + val_size >= len(images):
                raise ValueError(
                    f"Class {class_dir.name} has {len(images)} images, but "
                    f"train_shots_per_class={train_size} and val_shots_per_class={val_size} "
                    "leave no test samples."
                )
            train_pool = train_size + val_size
        else:
            train_pool = max(2, int(round(len(images) * protocol_train_ratio)))
            train_pool = min(train_pool, len(images) - 1)
            val_size = max(1, int(round(train_pool * val_ratio_from_train)))
            val_size = min(val_size, train_pool - 1)
            train_size = train_pool - val_size

        for index, image_path in enumerate(images):
            if index < train_size:
                split = "train"
            elif index < train_pool:
                split = "val"
            else:
                split = "test"

            rows.append(
                {
                    "split": split,
                    "class_name": class_dir.name,
                    "class_index": class_index,
                    "relative_path": str(image_path.relative_to(root)).replace("\\", "/"),
                }
            )

    manifest = pd.DataFrame(rows)
    manifest.to_csv(output_path, index=False)
    return output_path


def ensure_manifest(data_config: dict, seed: int) -> Path:
    root = Path(data_config["root"])
    manifest_path = Path(data_config["manifest_path"])
    if manifest_path.exists():
        return manifest_path

    if not root.exists():
        raise FileNotFoundError(
            f"Dataset root not found: {root}. Please place the dataset before training."
        )

    return create_manifest(
        root=root,
        output_path=manifest_path,
        protocol_train_ratio=float(data_config["protocol_train_ratio"]),
        val_ratio_from_train=float(data_config["val_ratio_from_train"]),
        seed=seed,
        extensions=data_config["extensions"],
        train_shots_per_class=data_config.get("train_shots_per_class"),
        val_shots_per_class=data_config.get("val_shots_per_class"),
    )


class ManifestImageDataset(Dataset):
    def __init__(
        self,
        root: str | Path,
        manifest_path: str | Path,
        split: str,
        transform,
    ) -> None:
        self.root = Path(root)
        frame = pd.read_csv(manifest_path)
        self.samples = frame[frame["split"] == split].reset_index(drop=True)
        if self.samples.empty:
            raise ValueError(f"Split {split} is empty in {manifest_path}")

        class_index_to_name = (
            frame[["class_index", "class_name"]]
            .drop_duplicates()
            .sort_values("class_index")
        )
        self.class_names = class_index_to_name["class_name"].tolist()
        self.transform = transform

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int):
        row = self.samples.iloc[index]
        image = Image.open(self.root / row["relative_path"]).convert("RGB")
        image = self.transform(image)
        label = int(row["class_index"])
        return image, label


def build_dataloaders(config: dict, seed: int):
    data_config = config["data"]
    manifest_path = ensure_manifest(data_config, seed)
    train_transform = build_train_transform(int(data_config["image_size"]))
    eval_transform = build_eval_transform(int(data_config["image_size"]))

    train_dataset = ManifestImageDataset(
        root=data_config["root"],
        manifest_path=manifest_path,
        split="train",
        transform=train_transform,
    )
    train_eval_dataset = ManifestImageDataset(
        root=data_config["root"],
        manifest_path=manifest_path,
        split="train",
        transform=eval_transform,
    )
    val_dataset = ManifestImageDataset(
        root=data_config["root"],
        manifest_path=manifest_path,
        split="val",
        transform=eval_transform,
    )
    test_dataset = ManifestImageDataset(
        root=data_config["root"],
        manifest_path=manifest_path,
        split="test",
        transform=eval_transform,
    )

    batch_size = int(data_config["batch_size"])
    num_workers = int(data_config["num_workers"])
    pin_memory = bool(data_config.get("pin_memory", True))

    loaders = {
        "train": DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=pin_memory,
        ),
        "train_eval": DataLoader(
            train_eval_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
        ),
        "val": DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
        ),
        "test": DataLoader(
            test_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=pin_memory,
        ),
    }

    info = {
        "class_names": train_dataset.class_names,
        "num_classes": len(train_dataset.class_names),
        "manifest_path": str(manifest_path),
        "protocol": {
            "train_shots_per_class": data_config.get("train_shots_per_class"),
            "val_shots_per_class": data_config.get("val_shots_per_class"),
            "train_ratio": data_config.get("protocol_train_ratio"),
            "val_ratio_from_train": data_config.get("val_ratio_from_train"),
        },
        "split_sizes": {
            "train": len(train_dataset),
            "val": len(val_dataset),
            "test": len(test_dataset),
        },
    }
    return loaders, info
