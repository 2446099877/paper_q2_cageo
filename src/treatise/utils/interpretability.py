from __future__ import annotations

from pathlib import Path
from typing import Sequence

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.nn.functional as F

from .visuals import denormalize_image


def compute_gradcam(
    model: torch.nn.Module,
    images: torch.Tensor,
    target_indices: torch.Tensor | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    model.eval()
    images = images.detach().clone().requires_grad_(True)
    outputs = model(images)
    feature_map = outputs["feature_map"]
    logits = outputs["logits"]

    if feature_map is not None and feature_map.requires_grad:
        feature_map.retain_grad()
    if target_indices is None:
        target_indices = logits.argmax(dim=1)

    selected_scores = logits.gather(1, target_indices.unsqueeze(1)).sum()
    model.zero_grad(set_to_none=True)
    selected_scores.backward()

    if feature_map is not None and feature_map.grad is not None:
        gradients = feature_map.grad
        weights = gradients.mean(dim=(2, 3), keepdim=True)
        cam = (weights * feature_map).sum(dim=1, keepdim=True)
        cam = F.relu(cam)
        cam = F.interpolate(cam, size=images.shape[-2:], mode="bilinear", align_corners=False)
    else:
        # Token backbones with CLS-only pooling may not expose gradients on the
        # returned spatial map. Fall back to a gradient saliency map so the
        # evaluation pipeline still produces usable qualitative evidence.
        image_grad = images.grad
        if image_grad is None:
            raise RuntimeError("No gradients available for interpretability visualization.")
        cam = image_grad.abs().mean(dim=1, keepdim=True)

    cam = cam.squeeze(1)
    cam_min = cam.amin(dim=(1, 2), keepdim=True)
    cam_max = cam.amax(dim=(1, 2), keepdim=True)
    cam = (cam - cam_min) / torch.clamp(cam_max - cam_min, min=1e-8)
    return cam.detach().cpu(), logits.detach().cpu()


def save_gradcam_grid(
    images: torch.Tensor,
    cams: torch.Tensor,
    targets: Sequence[int],
    predictions: Sequence[int],
    class_names: Sequence[str],
    output_path: str | Path,
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    images_np = images.detach().cpu().numpy()
    cams_np = cams.detach().cpu().numpy()

    num_samples = len(images_np)
    fig, axes = plt.subplots(num_samples, 2, figsize=(7, 3 * num_samples))
    if num_samples == 1:
        axes = np.array([axes])

    for idx in range(num_samples):
        base = denormalize_image(images_np[idx])
        heat = cams_np[idx]

        axes[idx, 0].imshow(base)
        axes[idx, 0].set_title(
            f"Image\nT={class_names[int(targets[idx])]} / P={class_names[int(predictions[idx])]}"
        )
        axes[idx, 0].axis("off")

        axes[idx, 1].imshow(base)
        axes[idx, 1].imshow(heat, cmap="jet", alpha=0.45)
        axes[idx, 1].set_title("Activation Map")
        axes[idx, 1].axis("off")

    fig.tight_layout()
    fig.savefig(output_path, dpi=200)
    plt.close(fig)
