from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd


def confusion_matrix(
    targets: Sequence[int],
    predictions: Sequence[int],
    num_classes: int,
) -> np.ndarray:
    matrix = np.zeros((num_classes, num_classes), dtype=np.int64)
    for target, prediction in zip(targets, predictions):
        matrix[int(target), int(prediction)] += 1
    return matrix


def summarize_classification(
    targets: Sequence[int],
    predictions: Sequence[int],
    class_names: Sequence[str],
) -> tuple[dict, np.ndarray, pd.DataFrame]:
    num_classes = len(class_names)
    matrix = confusion_matrix(targets, predictions, num_classes)
    total = matrix.sum()
    correct = np.trace(matrix)
    oa = float(correct / max(total, 1))

    row_sums = matrix.sum(axis=1)
    per_class_accuracy = np.divide(
        np.diag(matrix),
        np.maximum(row_sums, 1),
        dtype=np.float64,
    )
    aa = float(per_class_accuracy.mean())

    col_sums = matrix.sum(axis=0)
    expected = float((row_sums * col_sums).sum() / max(total * total, 1))
    kappa = float((oa - expected) / max(1.0 - expected, 1e-12))

    per_class_df = pd.DataFrame(
        {
            "class_name": list(class_names),
            "support": row_sums,
            "accuracy": per_class_accuracy,
        }
    )

    summary = {
        "oa": oa,
        "aa": aa,
        "kappa": kappa,
        "num_samples": int(total),
        "num_classes": num_classes,
    }
    return summary, matrix, per_class_df
