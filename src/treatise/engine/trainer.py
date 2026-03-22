from __future__ import annotations

import copy
import csv
import math
import random
from pathlib import Path

import pandas as pd
import torch
from torch import nn
from torch.nn import functional as F
from tqdm import tqdm

from treatise.engine.evaluator import evaluate_model, persist_evaluation
from treatise.utils.io import save_json


def _sample_beta(alpha: float) -> float:
    if alpha <= 0.0:
        return 1.0
    return float(torch.distributions.Beta(alpha, alpha).sample().item())


def apply_mixup_or_cutmix(
    images: torch.Tensor,
    labels: torch.Tensor,
    mixup_alpha: float,
    cutmix_alpha: float,
    probability: float,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, float]:
    if images.size(0) < 2 or random.random() > probability:
        return images, labels, labels, 1.0

    indices = torch.randperm(images.size(0), device=images.device)
    labels_b = labels[indices]

    use_cutmix = cutmix_alpha > 0.0 and (
        mixup_alpha <= 0.0 or random.random() < 0.5
    )

    if use_cutmix:
        lam = _sample_beta(cutmix_alpha)
        height, width = images.shape[-2:]
        cut_ratio = math.sqrt(1.0 - lam)
        cut_w = int(width * cut_ratio)
        cut_h = int(height * cut_ratio)

        center_x = random.randint(0, width - 1)
        center_y = random.randint(0, height - 1)
        x1 = max(center_x - cut_w // 2, 0)
        y1 = max(center_y - cut_h // 2, 0)
        x2 = min(center_x + cut_w // 2, width)
        y2 = min(center_y + cut_h // 2, height)

        mixed = images.clone()
        mixed[:, :, y1:y2, x1:x2] = images[indices, :, y1:y2, x1:x2]
        lam = 1.0 - ((x2 - x1) * (y2 - y1) / float(height * width))
        return mixed, labels, labels_b, float(lam)

    lam = _sample_beta(mixup_alpha)
    mixed = lam * images + (1.0 - lam) * images[indices]
    return mixed, labels, labels_b, float(lam)


def _save_checkpoint(
    model: nn.Module,
    optimizer: torch.optim.Optimizer,
    scheduler: torch.optim.lr_scheduler._LRScheduler,
    epoch: int,
    metrics: dict,
    class_names: list[str],
    output_path: str | Path,
) -> None:
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "scheduler_state_dict": scheduler.state_dict(),
            "epoch": epoch,
            "metrics": metrics,
            "class_names": class_names,
        },
        output_path,
    )


@torch.no_grad()
def _refresh_class_prototypes(
    model: nn.Module,
    data_loader,
    device: torch.device,
    num_classes: int,
) -> None:
    if data_loader is None or not hasattr(model, "set_class_prototypes"):
        return

    sums = None
    counts = torch.zeros(num_classes, device=device, dtype=torch.float32)
    model.eval()
    for images, labels in data_loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
        outputs = model(images)
        classifier_input = outputs.get("classifier_input", outputs["embedding"])
        features = F.normalize(classifier_input.float(), dim=1)

        if sums is None:
            sums = torch.zeros(num_classes, features.size(1), device=device, dtype=torch.float32)

        sums.index_add_(0, labels, features)
        counts.index_add_(0, labels, torch.ones_like(labels, dtype=torch.float32))

    if sums is None:
        return

    prototypes = sums / counts.clamp_min(1.0).unsqueeze(1)
    model.set_class_prototypes(prototypes, counts)


def fit(
    model: nn.Module,
    loaders: dict,
    config: dict,
    class_names: list[str],
    device: torch.device,
) -> dict:
    experiment = config["experiment"]
    training = config["training"]
    output_dir = Path(experiment["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    criterion = nn.CrossEntropyLoss(
        label_smoothing=float(training.get("label_smoothing", 0.0))
    )
    eval_criterion = nn.CrossEntropyLoss()
    trainable_params = [parameter for parameter in model.parameters() if parameter.requires_grad]
    if not trainable_params:
        raise RuntimeError("No trainable parameters found for the current configuration.")
    optimizer = torch.optim.AdamW(
        trainable_params,
        lr=float(training["learning_rate"]),
        betas=tuple(training.get("betas", [0.9, 0.999])),
        weight_decay=float(training["weight_decay"]),
    )
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer,
        T_max=int(training["epochs"]),
    )
    amp_enabled = bool(experiment.get("amp", True)) and device.type == "cuda"
    scaler = torch.amp.GradScaler("cuda", enabled=amp_enabled)
    grad_accum_steps = max(1, int(training.get("gradient_accumulation_steps", 1)))
    auxiliary_loss_weight = float(
        training.get("center_loss_weight", training.get("prototype_loss_weight", 0.0))
    )
    center_update_momentum = float(training.get("center_update_momentum", 0.9))
    refresh_prototypes = bool(training.get("refresh_prototypes_each_epoch", False))

    if refresh_prototypes:
        _refresh_class_prototypes(
            model=model,
            data_loader=loaders.get("train_eval"),
            device=device,
            num_classes=len(class_names),
        )

    history_path = output_dir / "history.csv"
    with history_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "epoch",
                "train_loss",
                "train_oa",
                "val_loss",
                "val_oa",
                "val_aa",
                "val_kappa",
                "lr",
            ],
        )
        writer.writeheader()

        best_state: dict | None = None
        best_oa = -1.0
        best_epoch = 0
        patience_counter = 0

        for epoch in range(1, int(training["epochs"]) + 1):
            model.train()
            running_loss = 0.0
            correct = 0
            total = 0
            optimizer.zero_grad(set_to_none=True)

            iterator = tqdm(loaders["train"], desc=f"epoch {epoch}", leave=False)
            num_batches = len(loaders["train"])
            for batch_index, (images, labels) in enumerate(iterator, start=1):
                images = images.to(device, non_blocking=True)
                labels = labels.to(device, non_blocking=True)

                mixed_images, labels_a, labels_b, lam = apply_mixup_or_cutmix(
                    images,
                    labels,
                    mixup_alpha=float(training.get("mixup_alpha", 0.0)),
                    cutmix_alpha=float(training.get("cutmix_alpha", 0.0)),
                    probability=float(training.get("mix_probability", 0.0)),
                )

                with torch.amp.autocast(device_type=device.type, enabled=amp_enabled):
                    outputs = model(mixed_images)
                    logits = outputs["logits"]
                    classifier_input = outputs.get("classifier_input", outputs["embedding"])
                    if lam == 1.0:
                        loss_logits = model.compute_training_logits(classifier_input, labels_a)
                        loss = criterion(loss_logits, labels_a)
                        if auxiliary_loss_weight > 0.0:
                            loss = loss + auxiliary_loss_weight * model.prototype_alignment_loss(
                                classifier_input,
                                labels_a,
                            )
                    else:
                        loss_logits_a = model.compute_training_logits(classifier_input, labels_a)
                        loss_logits_b = model.compute_training_logits(classifier_input, labels_b)
                        loss = lam * criterion(loss_logits_a, labels_a) + (1.0 - lam) * criterion(
                            loss_logits_b,
                            labels_b,
                        )
                        if auxiliary_loss_weight > 0.0:
                            loss = loss + auxiliary_loss_weight * (
                                lam * model.prototype_alignment_loss(classifier_input, labels_a)
                                + (1.0 - lam)
                                * model.prototype_alignment_loss(classifier_input, labels_b)
                            )

                loss_value = float(loss.item())
                loss_to_backprop = loss / grad_accum_steps
                scaler.scale(loss_to_backprop).backward()

                should_step = batch_index % grad_accum_steps == 0 or batch_index == num_batches
                if should_step:
                    if training.get("gradient_clip_norm", 0.0):
                        scaler.unscale_(optimizer)
                        torch.nn.utils.clip_grad_norm_(
                            trainable_params,
                            max_norm=float(training["gradient_clip_norm"]),
                        )
                    scaler.step(optimizer)
                    scaler.update()
                    optimizer.zero_grad(set_to_none=True)
                if lam == 1.0:
                    model.update_class_centers(
                        classifier_input.detach(),
                        labels_a,
                        momentum=center_update_momentum,
                    )

                preds = logits.argmax(dim=1)
                running_loss += loss_value * labels.size(0)
                correct += int((preds == labels).sum().item())
                total += int(labels.size(0))

            scheduler.step()

            if refresh_prototypes:
                _refresh_class_prototypes(
                    model=model,
                    data_loader=loaders.get("train_eval"),
                    device=device,
                    num_classes=len(class_names),
                )

            train_loss = running_loss / max(total, 1)
            train_oa = correct / max(total, 1)
            val_summary, _, _ = evaluate_model(
                model,
                loaders["val"],
                device=device,
                class_names=class_names,
                criterion=eval_criterion,
            )

            row = {
                "epoch": epoch,
                "train_loss": train_loss,
                "train_oa": train_oa,
                "val_loss": val_summary.get("loss", 0.0),
                "val_oa": val_summary["oa"],
                "val_aa": val_summary["aa"],
                "val_kappa": val_summary["kappa"],
                "lr": optimizer.param_groups[0]["lr"],
            }
            writer.writerow(row)
            handle.flush()

            _save_checkpoint(
                model,
                optimizer,
                scheduler,
                epoch,
                val_summary,
                class_names,
                output_dir / "last.pt",
            )

            improved = val_summary["oa"] > best_oa + float(training.get("min_delta", 0.0))
            if improved:
                best_oa = val_summary["oa"]
                best_epoch = epoch
                patience_counter = 0
                best_state = {
                    "model": copy.deepcopy(model.state_dict()),
                    "metrics": copy.deepcopy(val_summary),
                }
                _save_checkpoint(
                    model,
                    optimizer,
                    scheduler,
                    epoch,
                    val_summary,
                    class_names,
                    output_dir / "best.pt",
                )
            else:
                patience_counter += 1

            if patience_counter >= int(training.get("patience", 10)):
                break

    if best_state is None:
        raise RuntimeError("Training finished without a valid checkpoint.")

    model.load_state_dict(best_state["model"])
    val_summary, val_matrix, val_df = evaluate_model(
        model,
        loaders["val"],
        device=device,
        class_names=class_names,
        criterion=eval_criterion,
    )
    test_summary, test_matrix, test_df = evaluate_model(
        model,
        loaders["test"],
        device=device,
        class_names=class_names,
        criterion=eval_criterion,
    )

    persist_evaluation(val_summary, val_matrix, val_df, class_names, output_dir, prefix="val")
    persist_evaluation(test_summary, test_matrix, test_df, class_names, output_dir, prefix="test")

    history = pd.read_csv(history_path)
    summary = {
        "experiment_name": experiment["name"],
        "run_name": experiment["run_name"],
        "seed": int(experiment["seed"]),
        "output_dir": str(output_dir),
        "best_epoch": best_epoch,
        "history_path": str(history_path),
        "num_epochs_completed": int(len(history)),
        "val": val_summary,
        "test": test_summary,
        "class_names": class_names,
    }
    save_json(summary, output_dir / "summary.json")
    return summary
