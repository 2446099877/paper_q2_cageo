from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable


def save_json(payload: dict, output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def load_json(input_path: str | Path) -> dict:
    input_path = Path(input_path)
    with input_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_csv_rows(
    rows: Iterable[dict],
    output_path: str | Path,
    fieldnames: list[str],
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
