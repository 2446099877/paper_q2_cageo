from __future__ import annotations

import torch
from torch import nn
from torch.nn import functional as F


class MultiScaleContextAggregator(nn.Module):
    def __init__(
        self,
        channels: int,
        reduction: int = 4,
        kernels: tuple[int, ...] = (3, 5, 7),
    ) -> None:
        super().__init__()
        hidden = max(channels // reduction, 64)
        self.reduce = nn.Sequential(
            nn.Conv2d(channels, hidden, kernel_size=1, bias=False),
            nn.BatchNorm2d(hidden),
            nn.GELU(),
        )
        self.branches = nn.ModuleList(
            [
                nn.Sequential(
                    nn.Conv2d(
                        hidden,
                        hidden,
                        kernel_size=kernel,
                        padding=kernel // 2,
                        groups=hidden,
                        bias=False,
                    ),
                    nn.BatchNorm2d(hidden),
                    nn.GELU(),
                )
                for kernel in kernels
            ]
        )
        self.global_branch = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Conv2d(hidden, hidden, kernel_size=1, bias=False),
            nn.GELU(),
        )
        self.fuse = nn.Sequential(
            nn.Conv2d(hidden * (len(kernels) + 1), channels, kernel_size=1, bias=False),
            nn.BatchNorm2d(channels),
            nn.GELU(),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        reduced = self.reduce(x)
        height, width = reduced.shape[-2:]
        multi_scale = [branch(reduced) for branch in self.branches]
        global_context = self.global_branch(reduced).expand(-1, -1, height, width)
        fused = self.fuse(torch.cat(multi_scale + [global_context], dim=1))
        return x + fused


class LocalGlobalFusionHead(nn.Module):
    def __init__(self, channels: int, reduction: int = 4, dropout: float = 0.2) -> None:
        super().__init__()
        hidden = max(channels // reduction, 64)
        self.local_branch = nn.Sequential(
            nn.Conv2d(
                channels,
                channels,
                kernel_size=3,
                padding=1,
                groups=channels,
                bias=False,
            ),
            nn.BatchNorm2d(channels),
            nn.GELU(),
        )
        self.global_gate = nn.Sequential(
            nn.Linear(channels, hidden),
            nn.GELU(),
            nn.Linear(hidden, channels),
            nn.Sigmoid(),
        )
        self.proj = nn.Sequential(
            nn.Linear(channels, channels),
            nn.GELU(),
            nn.Dropout(dropout),
        )
        self.norm = nn.LayerNorm(channels)

    def forward(self, pooled: torch.Tensor, feature_map: torch.Tensor) -> torch.Tensor:
        local = F.adaptive_avg_pool2d(self.local_branch(feature_map), 1).flatten(1)
        gate = self.global_gate(pooled)
        fused = pooled + gate * local
        return self.norm(pooled + self.proj(fused))


class SalientGlobalFusionHead(nn.Module):
    def __init__(
        self,
        channels: int,
        topk_ratio: float = 0.25,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        if not 0.0 < topk_ratio <= 1.0:
            raise ValueError("topk_ratio must be in the range (0, 1].")

        self.topk_ratio = float(topk_ratio)
        self.salient_norm = nn.LayerNorm(channels)
        self.gate_scale = nn.Parameter(torch.ones(channels))
        self.gate_bias = nn.Parameter(torch.zeros(channels))
        self.residual_scale = nn.Parameter(torch.full((channels,), 0.1))
        self.dropout = nn.Dropout(dropout)
        self.out_norm = nn.LayerNorm(channels)

    def forward(self, pooled: torch.Tensor, feature_map: torch.Tensor) -> torch.Tensor:
        pooled_fp = pooled.float()
        spatial_tokens = feature_map.float().flatten(2)
        num_tokens = int(spatial_tokens.size(-1))
        topk = max(1, min(num_tokens, int(round(num_tokens * self.topk_ratio))))
        salient = spatial_tokens.topk(k=topk, dim=-1).values.mean(dim=-1)
        salient = self.salient_norm(salient)

        delta = salient - pooled_fp
        gate = torch.sigmoid(
            self.gate_scale.float() * salient + self.gate_bias.float()
        )
        fused = pooled_fp + self.dropout(self.residual_scale.float() * gate * delta)
        return self.out_norm(fused).to(pooled.dtype)


class AdaptiveGeMFusionHead(nn.Module):
    def __init__(
        self,
        channels: int,
        p_init: float = 3.0,
        dropout: float = 0.0,
        eps: float = 1e-6,
    ) -> None:
        super().__init__()
        self.eps = float(eps)
        self.p = nn.Parameter(torch.tensor([p_init], dtype=torch.float32))
        self.mix_logit = nn.Parameter(torch.tensor([-2.0], dtype=torch.float32))
        self.gem_norm = nn.LayerNorm(channels)
        self.dropout = nn.Dropout(dropout)
        self.out_norm = nn.LayerNorm(channels)

    def forward(self, pooled: torch.Tensor, feature_map: torch.Tensor) -> torch.Tensor:
        pooled_fp = pooled.float()
        p = self.p.clamp(min=1.0, max=6.0)
        gem_map = feature_map.float().clamp(min=self.eps).pow(p.view(1, 1, 1, 1))
        gem = F.adaptive_avg_pool2d(gem_map, 1).pow(1.0 / p).flatten(1)
        gem = self.gem_norm(gem)

        mix = torch.sigmoid(self.mix_logit).view(1, 1)
        fused = pooled_fp + mix * (gem - pooled_fp)
        return self.out_norm(self.dropout(fused)).to(pooled.dtype)


class CosineClassifier(nn.Module):
    def __init__(
        self,
        in_features: int,
        num_classes: int,
        scale: float = 30.0,
        learn_scale: bool = False,
    ) -> None:
        super().__init__()
        self.weight = nn.Parameter(torch.empty(num_classes, in_features))
        nn.init.xavier_uniform_(self.weight)

        if learn_scale:
            self.scale = nn.Parameter(torch.tensor([scale], dtype=torch.float32))
        else:
            self.register_buffer("scale", torch.tensor([scale], dtype=torch.float32))

    def _cosine_logits(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        features = F.normalize(x.float(), dim=1)
        weights = F.normalize(self.weight.float(), dim=1)
        cosine = F.linear(features, weights)
        scale = self.scale.float().clamp(min=1.0, max=64.0)
        return cosine, scale.view(1, 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        cosine, scale = self._cosine_logits(x)
        return (scale * cosine).to(x.dtype)


class AngularMarginCosineClassifier(CosineClassifier):
    def __init__(
        self,
        in_features: int,
        num_classes: int,
        scale: float = 30.0,
        margin: float = 0.15,
        learn_scale: bool = False,
    ) -> None:
        super().__init__(
            in_features=in_features,
            num_classes=num_classes,
            scale=scale,
            learn_scale=learn_scale,
        )
        self.margin = float(margin)

    def forward_with_margin(self, x: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        cosine, scale = self._cosine_logits(x)
        one_hot = F.one_hot(labels, num_classes=cosine.size(1)).to(cosine.dtype)
        margin_logits = cosine - one_hot * self.margin
        return (scale * margin_logits).to(x.dtype)


class CenterRegularizedCosineClassifier(CosineClassifier):
    def __init__(
        self,
        in_features: int,
        num_classes: int,
        scale: float = 30.0,
        learn_scale: bool = False,
    ) -> None:
        super().__init__(
            in_features=in_features,
            num_classes=num_classes,
            scale=scale,
            learn_scale=learn_scale,
        )
        self.register_buffer("centers", torch.zeros(num_classes, in_features, dtype=torch.float32))
        self.register_buffer("center_counts", torch.zeros(num_classes, dtype=torch.float32))

    @torch.no_grad()
    def update_centers(
        self,
        x: torch.Tensor,
        labels: torch.Tensor,
        momentum: float = 0.9,
    ) -> None:
        features = F.normalize(x.detach().float(), dim=1)
        unique_labels = labels.unique()
        momentum = float(momentum)

        for class_index in unique_labels.tolist():
            mask = labels == class_index
            batch_center = features[mask].mean(dim=0)
            if float(self.center_counts[class_index].item()) > 0:
                batch_center = momentum * self.centers[class_index] + (1.0 - momentum) * batch_center
            self.centers[class_index] = F.normalize(batch_center.unsqueeze(0), dim=1).squeeze(0)
            self.center_counts[class_index] += float(mask.sum().item())

    def clear_centers(self) -> None:
        self.centers.zero_()
        self.center_counts.zero_()

    def prototype_alignment_loss(self, x: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        valid = self.center_counts[labels] > 0
        if not bool(valid.any()):
            return x.new_tensor(0.0)

        features = F.normalize(x.float(), dim=1)
        target_centers = F.normalize(self.centers[labels].float(), dim=1)
        loss = 1.0 - (features[valid] * target_centers[valid]).sum(dim=1)
        return loss.mean().to(x.dtype)


class FeatureCenterBank(nn.Module):
    def __init__(self, in_features: int, num_classes: int) -> None:
        super().__init__()
        self.register_buffer("centers", torch.zeros(num_classes, in_features, dtype=torch.float32))
        self.register_buffer("center_counts", torch.zeros(num_classes, dtype=torch.float32))

    @torch.no_grad()
    def update_centers(
        self,
        x: torch.Tensor,
        labels: torch.Tensor,
        momentum: float = 0.9,
    ) -> None:
        features = F.normalize(x.detach().float(), dim=1)
        unique_labels = labels.unique()
        momentum = float(momentum)

        for class_index in unique_labels.tolist():
            mask = labels == class_index
            batch_center = features[mask].mean(dim=0)
            if float(self.center_counts[class_index].item()) > 0:
                batch_center = momentum * self.centers[class_index] + (1.0 - momentum) * batch_center
            self.centers[class_index] = F.normalize(batch_center.unsqueeze(0), dim=1).squeeze(0)
            self.center_counts[class_index] += float(mask.sum().item())

    def clear_centers(self) -> None:
        self.centers.zero_()
        self.center_counts.zero_()

    def alignment_loss(self, x: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        valid = self.center_counts[labels] > 0
        if not bool(valid.any()):
            return x.new_tensor(0.0)

        features = F.normalize(x.float(), dim=1)
        target_centers = F.normalize(self.centers[labels].float(), dim=1)
        loss = 1.0 - (features[valid] * target_centers[valid]).sum(dim=1)
        return loss.mean().to(x.dtype)


class ResidualFeatureAdapter(nn.Module):
    def __init__(
        self,
        in_features: int,
        hidden_features: int,
        dropout: float = 0.1,
    ) -> None:
        super().__init__()
        self.norm = nn.LayerNorm(in_features)
        self.fc1 = nn.Linear(in_features, hidden_features)
        self.act = nn.GELU()
        self.fc2 = nn.Linear(hidden_features, in_features)
        self.dropout = nn.Dropout(dropout)
        self.scale = nn.Parameter(torch.tensor([0.1], dtype=torch.float32))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        residual = self.fc2(self.dropout(self.act(self.fc1(self.norm(x.float())))))
        return (x.float() + self.scale.float().view(1, 1) * residual).to(x.dtype)


class PrototypeRegularizedCosineClassifier(nn.Module):
    def __init__(
        self,
        in_features: int,
        num_classes: int,
        scale: float = 30.0,
        learn_scale: bool = False,
    ) -> None:
        super().__init__()
        self.weight = nn.Parameter(torch.empty(num_classes, in_features))
        nn.init.xavier_uniform_(self.weight)

        if learn_scale:
            self.scale = nn.Parameter(torch.tensor([scale], dtype=torch.float32))
        else:
            self.register_buffer("scale", torch.tensor([scale], dtype=torch.float32))
        self.register_buffer("prototypes", torch.zeros(num_classes, in_features, dtype=torch.float32))
        self.register_buffer("prototype_counts", torch.zeros(num_classes, dtype=torch.float32))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = F.normalize(x.float(), dim=1)
        weights = F.normalize(self.weight.float(), dim=1)
        cosine = F.linear(features, weights)
        scale = self.scale.float().clamp(min=1.0, max=64.0)
        return (scale.view(1, 1) * cosine).to(x.dtype)

    def set_prototypes(
        self,
        prototypes: torch.Tensor,
        counts: torch.Tensor | None = None,
    ) -> None:
        self.prototypes.copy_(prototypes.float())
        if counts is None:
            counts = (prototypes.norm(dim=1) > 0).float()
        self.prototype_counts.copy_(counts.float())

    def clear_prototypes(self) -> None:
        self.prototypes.zero_()
        self.prototype_counts.zero_()

    def prototype_alignment_loss(self, x: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        valid = self.prototype_counts[labels] > 0
        if not bool(valid.any()):
            return x.new_tensor(0.0)

        features = F.normalize(x.float(), dim=1)
        target_prototypes = F.normalize(self.prototypes[labels].float(), dim=1)
        loss = 1.0 - (features[valid] * target_prototypes[valid]).sum(dim=1)
        return loss.mean().to(x.dtype)


class PrototypeCalibratedCosineClassifier(nn.Module):
    def __init__(
        self,
        in_features: int,
        num_classes: int,
        scale: float = 30.0,
        prototype_scale: float = 30.0,
        mix_init: float = -2.0,
        learn_scale: bool = False,
    ) -> None:
        super().__init__()
        self.weight = nn.Parameter(torch.empty(num_classes, in_features))
        nn.init.xavier_uniform_(self.weight)

        if learn_scale:
            self.scale = nn.Parameter(torch.tensor([scale], dtype=torch.float32))
        else:
            self.register_buffer("scale", torch.tensor([scale], dtype=torch.float32))
        self.register_buffer("prototype_scale", torch.tensor([prototype_scale], dtype=torch.float32))
        self.mix_logit = nn.Parameter(torch.tensor([mix_init], dtype=torch.float32))
        self.register_buffer("prototypes", torch.zeros(num_classes, in_features, dtype=torch.float32))
        self.register_buffer("prototype_counts", torch.zeros(num_classes, dtype=torch.float32))

    def _classifier_logits(self, x: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        features = F.normalize(x.float(), dim=1)
        weights = F.normalize(self.weight.float(), dim=1)
        cosine = F.linear(features, weights)
        scale = self.scale.float().clamp(min=1.0, max=64.0)
        return scale.view(1, 1) * cosine, features

    def _prototype_logits(self, features: torch.Tensor) -> torch.Tensor | None:
        valid = self.prototype_counts > 0
        if not bool(valid.any()):
            return None

        normalized_prototypes = F.normalize(self.prototypes[valid].float(), dim=1)
        prototype_logits = features.new_zeros(features.size(0), self.prototypes.size(0))
        prototype_logits[:, valid] = self.prototype_scale.float().clamp(min=1.0, max=64.0).view(
            1, 1
        ) * F.linear(features, normalized_prototypes)
        return prototype_logits

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        classifier_logits, features = self._classifier_logits(x)
        prototype_logits = self._prototype_logits(features)
        if prototype_logits is None:
            return classifier_logits.to(x.dtype)

        mix = torch.sigmoid(self.mix_logit.float()).view(1, 1)
        logits = (1.0 - mix) * classifier_logits + mix * prototype_logits
        return logits.to(x.dtype)

    def set_prototypes(
        self,
        prototypes: torch.Tensor,
        counts: torch.Tensor | None = None,
    ) -> None:
        self.prototypes.copy_(prototypes.float())
        if counts is None:
            counts = (prototypes.norm(dim=1) > 0).float()
        self.prototype_counts.copy_(counts.float())

    def clear_prototypes(self) -> None:
        self.prototypes.zero_()
        self.prototype_counts.zero_()

    def prototype_alignment_loss(self, x: torch.Tensor, labels: torch.Tensor) -> torch.Tensor:
        valid = self.prototype_counts[labels] > 0
        if not bool(valid.any()):
            return x.new_tensor(0.0)

        features = F.normalize(x.float(), dim=1)
        target_prototypes = F.normalize(self.prototypes[labels].float(), dim=1)
        loss = 1.0 - (features[valid] * target_prototypes[valid]).sum(dim=1)
        return loss.mean().to(x.dtype)
