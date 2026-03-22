from __future__ import annotations

from pathlib import Path
from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


def plot_confusion_matrix(
    matrix: np.ndarray,
    class_names: Sequence[str],
    output_path: str | Path,
    max_labels: int = 15,
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    labels = list(class_names)
    display_matrix = matrix
    if len(labels) > max_labels:
        labels = labels[:max_labels]
        display_matrix = matrix[:max_labels, :max_labels]

    plt.figure(figsize=(10, 8))
    sns.heatmap(display_matrix, cmap="Blues", annot=False, xticklabels=labels, yticklabels=labels)
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_metric_bars(summary_df: pd.DataFrame, output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4))
    metrics = ["oa", "aa", "kappa"]
    titles = ["Overall Accuracy", "Average Accuracy", "Kappa"]
    for axis, metric, title in zip(axes, metrics, titles):
        axis.bar(summary_df["run"], summary_df[metric], color="#3A6EA5")
        axis.set_title(title)
        axis.set_ylim(0.0, 1.0)
        axis.tick_params(axis="x", rotation=20)
    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)


def denormalize_image(image: np.ndarray) -> np.ndarray:
    image = image.transpose(1, 2, 0)
    image = image * IMAGENET_STD + IMAGENET_MEAN
    return np.clip(image, 0.0, 1.0)
