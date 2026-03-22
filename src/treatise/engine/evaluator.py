from __future__ import annotations

from pathlib import Path

import pandas as pd
import torch
from tqdm import tqdm

from treatise.utils.io import save_json
from treatise.utils.metrics import summarize_classification
from treatise.utils.visuals import plot_confusion_matrix


@torch.no_grad()
def evaluate_model(
    model: torch.nn.Module,
    data_loader,
    device: torch.device,
    class_names: list[str],
    criterion: torch.nn.Module | None = None,
    progress: bool = False,
) -> tuple[dict, torch.Tensor, pd.DataFrame]:
    model.eval()
    losses: list[float] = []
    targets: list[int] = []
    predictions: list[int] = []

    iterator = tqdm(data_loader, desc="eval", leave=False) if progress else data_loader
    for images, labels in iterator:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        outputs = model(images)
        logits = outputs["logits"]

        if criterion is not None:
            losses.append(float(criterion(logits, labels).item()))

        preds = logits.argmax(dim=1)
        targets.extend(labels.cpu().tolist())
        predictions.extend(preds.cpu().tolist())

    summary, matrix, class_df = summarize_classification(targets, predictions, class_names)
    if losses:
        summary["loss"] = float(sum(losses) / len(losses))
    return summary, torch.from_numpy(matrix), class_df


def persist_evaluation(
    summary: dict,
    matrix: torch.Tensor,
    class_df: pd.DataFrame,
    class_names: list[str],
    output_dir: str | Path,
    prefix: str,
) -> None:
    output_dir = Path(output_dir)
    save_json(summary, output_dir / f"{prefix}_summary.json")
    class_df.to_csv(output_dir / f"{prefix}_class_metrics.csv", index=False)
    plot_confusion_matrix(
        matrix.numpy(),
        class_names,
        output_dir / f"{prefix}_confusion_matrix.png",
    )
