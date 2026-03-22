from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

import yaml


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if (
            key in merged
            and isinstance(merged[key], dict)
            and isinstance(value, dict)
        ):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def load_config(config_path: str | Path) -> dict[str, Any]:
    config_path = Path(config_path).resolve()
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}

    base_path = config.pop("base", None)
    if base_path:
        parent_config = load_config(config_path.parent / base_path)
        return deep_merge(parent_config, config)
    return config


def finalize_config(
    config: dict[str, Any],
    config_path: str | Path,
    seed: int | None = None,
) -> dict[str, Any]:
    config_path = Path(config_path).resolve()
    project_root = discover_project_root(config_path)
    resolved = copy.deepcopy(config)

    experiment = resolved.setdefault("experiment", {})
    data = resolved.setdefault("data", {})

    runtime_seed = int(seed if seed is not None else experiment.get("seed", 3407))
    experiment["seed"] = runtime_seed

    output_root = project_root / experiment.get("output_root", "outputs")
    output_dir = (
        output_root
        / experiment.get("name", "experiment")
        / experiment.get("run_name", "baseline")
        / f"seed_{runtime_seed}"
    )
    experiment["output_dir"] = str(output_dir)
    experiment["project_root"] = str(project_root)
    experiment["config_path"] = str(config_path)

    data["root"] = str(project_root / data.get("root", "data/raw/AID"))
    data["manifest_dir"] = str(project_root / data.get("manifest_dir", "data/splits"))
    dataset_name = data.get("dataset_name", "dataset").lower().replace("-", "_")
    train_shots = data.get("train_shots_per_class")
    val_shots = data.get("val_shots_per_class")
    if train_shots is not None:
        val_shots = int(
            val_shots
            if val_shots is not None
            else max(1, int(round(int(train_shots) * float(data.get("val_ratio_from_train", 0.1)))))
        )
        manifest_name = f"{dataset_name}_shot{int(train_shots)}_val{val_shots}_seed{runtime_seed}.csv"
    else:
        train_ratio = int(round(float(data.get("protocol_train_ratio", 0.2)) * 100))
        manifest_name = f"{dataset_name}_tr{train_ratio}_seed{runtime_seed}.csv"
    data["manifest_path"] = str(Path(data["manifest_dir"]) / manifest_name)
    return resolved


def discover_project_root(config_path: str | Path) -> Path:
    config_path = Path(config_path).resolve()
    candidates = [config_path.parent, *config_path.parents]
    for candidate in candidates:
        if (candidate / "src" / "treatise").exists() and (candidate / "configs").exists():
            return candidate
    raise FileNotFoundError(f"Could not determine project root from {config_path}")


def dump_yaml(config: dict[str, Any], output_path: str | Path) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as handle:
        yaml.safe_dump(config, handle, sort_keys=False, allow_unicode=True)
