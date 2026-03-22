from __future__ import annotations

import math

import torch
from torch import nn
from torchvision.models import ConvNeXt_Tiny_Weights, convnext_tiny
from transformers import Dinov2Config, Dinov2Model

from .modules import (
    AdaptiveGeMFusionHead,
    AngularMarginCosineClassifier,
    CenterRegularizedCosineClassifier,
    CosineClassifier,
    FeatureCenterBank,
    LocalGlobalFusionHead,
    MultiScaleContextAggregator,
    PrototypeCalibratedCosineClassifier,
    PrototypeRegularizedCosineClassifier,
    ResidualFeatureAdapter,
    SalientGlobalFusionHead,
)


class RSSceneClassifier(nn.Module):
    def __init__(self, model_config: dict, num_classes: int) -> None:
        super().__init__()
        self.backbone_name = model_config.get("backbone", "convnext_tiny")
        self.freeze_backbone = bool(model_config.get("freeze_backbone", False))
        self.uses_token_backbone = False
        self.token_pooling = str(model_config.get("token_pooling", "cls"))

        if self.backbone_name == "convnext_tiny":
            feature_dim = self._init_convnext_backbone(model_config)
        elif self.backbone_name in {"dinov2_small", "dinov2_base"}:
            feature_dim = self._init_dinov2_backbone(model_config)
        else:
            raise ValueError(
                f"Unsupported backbone: {self.backbone_name}. "
                "Expected one of ['convnext_tiny', 'dinov2_small', 'dinov2_base']."
            )

        self.dropout = nn.Dropout(float(model_config.get("dropout", 0.2)))
        adapter_dim = int(model_config.get("adapter_dim", 0))
        self.feature_adapter = (
            ResidualFeatureAdapter(
                in_features=feature_dim,
                hidden_features=adapter_dim,
                dropout=float(model_config.get("adapter_dropout", 0.1)),
            )
            if adapter_dim > 0
            else None
        )
        self.use_cosine = bool(model_config.get("use_cosine", False))
        self.use_amcc = bool(model_config.get("use_amcc", False))
        self.use_center_reg = bool(model_config.get("use_center_reg", False))
        self.use_feature_center_reg = bool(model_config.get("use_feature_center_reg", False))
        self.use_proto_reg = bool(model_config.get("use_proto_reg", False))
        self.use_proto_calib = bool(model_config.get("use_proto_calib", False))
        self.center_memory = (
            FeatureCenterBank(in_features=feature_dim, num_classes=num_classes)
            if self.use_feature_center_reg
            else None
        )
        if self.use_cosine:
            self.classifier = CosineClassifier(
                in_features=feature_dim,
                num_classes=num_classes,
                scale=float(model_config.get("cosine_scale", 30.0)),
                learn_scale=bool(model_config.get("cosine_learn_scale", False)),
            )
        elif self.use_center_reg:
            self.classifier = CenterRegularizedCosineClassifier(
                in_features=feature_dim,
                num_classes=num_classes,
                scale=float(model_config.get("center_reg_scale", 30.0)),
                learn_scale=bool(model_config.get("center_reg_learn_scale", False)),
            )
        elif self.use_proto_reg:
            self.classifier = PrototypeRegularizedCosineClassifier(
                in_features=feature_dim,
                num_classes=num_classes,
                scale=float(model_config.get("proto_reg_scale", 30.0)),
                learn_scale=bool(model_config.get("proto_reg_learn_scale", False)),
            )
        elif self.use_proto_calib:
            self.classifier = PrototypeCalibratedCosineClassifier(
                in_features=feature_dim,
                num_classes=num_classes,
                scale=float(model_config.get("proto_calib_scale", 30.0)),
                prototype_scale=float(model_config.get("proto_calib_prototype_scale", 30.0)),
                mix_init=float(model_config.get("proto_calib_mix_init", -2.0)),
                learn_scale=bool(model_config.get("proto_calib_learn_scale", False)),
            )
        elif self.use_amcc:
            self.classifier = AngularMarginCosineClassifier(
                in_features=feature_dim,
                num_classes=num_classes,
                scale=float(model_config.get("amcc_scale", 30.0)),
                margin=float(model_config.get("amcc_margin", 0.15)),
                learn_scale=bool(model_config.get("amcc_learn_scale", False)),
            )
        else:
            self.classifier = nn.Linear(feature_dim, num_classes)

    def _init_convnext_backbone(self, model_config: dict) -> int:
        weights = (
            ConvNeXt_Tiny_Weights.IMAGENET1K_V1
            if model_config.get("pretrained", True)
            else None
        )
        backbone = convnext_tiny(weights=weights)
        self.features = backbone.features
        if self.freeze_backbone:
            for parameter in self.features.parameters():
                parameter.requires_grad = False

        feature_dim = backbone.classifier[-1].in_features
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.norm = nn.LayerNorm(feature_dim)

        if model_config.get("use_msca", False):
            kernels = tuple(model_config.get("msca_kernels", [3, 5, 7]))
            self.context_module = MultiScaleContextAggregator(
                channels=feature_dim,
                reduction=int(model_config.get("msca_reduction", 4)),
                kernels=kernels,
            )
        else:
            self.context_module = nn.Identity()

        if model_config.get("use_lgfh", False):
            self.fusion_head = LocalGlobalFusionHead(
                channels=feature_dim,
                reduction=int(model_config.get("head_reduction", 4)),
                dropout=float(model_config.get("dropout", 0.2)),
            )
        elif model_config.get("use_agfh", False):
            self.fusion_head = AdaptiveGeMFusionHead(
                channels=feature_dim,
                p_init=float(model_config.get("agfh_p_init", 3.0)),
                dropout=float(model_config.get("agfh_dropout", 0.0)),
            )
        elif model_config.get("use_sgfh", False):
            self.fusion_head = SalientGlobalFusionHead(
                channels=feature_dim,
                topk_ratio=float(model_config.get("sgfh_topk_ratio", 0.25)),
                dropout=float(model_config.get("sgfh_dropout", model_config.get("dropout", 0.2))),
            )
        else:
            self.fusion_head = None
        return feature_dim

    def _init_dinov2_backbone(self, model_config: dict) -> int:
        self.uses_token_backbone = True
        default_model_name = {
            "dinov2_small": "facebook/dinov2-small",
            "dinov2_base": "facebook/dinov2-base",
        }.get(self.backbone_name, "facebook/dinov2-small")
        model_name = model_config.get("pretrained_model_name", default_model_name)
        if model_config.get("pretrained", True):
            self.backbone = Dinov2Model.from_pretrained(model_name)
        else:
            config = Dinov2Config(
                image_size=int(model_config.get("image_size", 224)),
                patch_size=int(model_config.get("dinov2_patch_size", 14)),
                hidden_size=int(model_config.get("dinov2_hidden_size", 384)),
                num_hidden_layers=int(model_config.get("dinov2_num_hidden_layers", 12)),
                num_attention_heads=int(model_config.get("dinov2_num_attention_heads", 6)),
                intermediate_size=int(model_config.get("dinov2_intermediate_size", 1536)),
            )
            self.backbone = Dinov2Model(config)

        if bool(model_config.get("gradient_checkpointing", False)) and hasattr(
            self.backbone, "gradient_checkpointing_enable"
        ):
            self.backbone.gradient_checkpointing_enable()
            # Gradient checkpointing on partially frozen backbones needs gradient
            # carrying inputs, otherwise the unfrozen tail blocks receive no grads.
            if hasattr(self.backbone, "enable_input_require_grads"):
                self.backbone.enable_input_require_grads()

        if self.freeze_backbone:
            for parameter in self.backbone.parameters():
                parameter.requires_grad = False

            unfreeze_last_n = int(model_config.get("unfreeze_last_n_blocks", 0))
            if unfreeze_last_n > 0 and hasattr(self.backbone.encoder, "layer"):
                for block in self.backbone.encoder.layer[-unfreeze_last_n:]:
                    for parameter in block.parameters():
                        parameter.requires_grad = True
            if bool(model_config.get("unfreeze_backbone_norm", True)) and hasattr(
                self.backbone, "layernorm"
            ):
                for parameter in self.backbone.layernorm.parameters():
                    parameter.requires_grad = True

        feature_dim = int(self.backbone.config.hidden_size)
        self.context_module = nn.Identity()
        self.fusion_head = None
        self.pool = None
        self.norm = nn.LayerNorm(feature_dim)
        return feature_dim

    def forward_features(self, x):
        if self.uses_token_backbone:
            if self.freeze_backbone and not any(
                parameter.requires_grad for parameter in self.backbone.parameters()
            ):
                with torch.no_grad():
                    outputs = self.backbone(pixel_values=x)
            else:
                outputs = self.backbone(pixel_values=x)

            tokens = outputs.last_hidden_state
            cls_token = tokens[:, 0]
            patch_tokens = tokens[:, 1:]
            if self.token_pooling == "cls":
                pooled_tokens = cls_token
            elif self.token_pooling == "mean":
                pooled_tokens = patch_tokens.mean(dim=1)
            elif self.token_pooling == "cls_mean":
                pooled_tokens = 0.5 * (cls_token + patch_tokens.mean(dim=1))
            else:
                raise ValueError(
                    f"Unsupported token_pooling: {self.token_pooling}. "
                    "Expected one of ['cls', 'mean', 'cls_mean']."
                )
            if self.feature_adapter is not None:
                pooled_tokens = self.feature_adapter(pooled_tokens)
            embedding = self.norm(pooled_tokens)

            spatial_dim = int(round(math.sqrt(patch_tokens.size(1))))
            if spatial_dim * spatial_dim == patch_tokens.size(1):
                feature_map = patch_tokens.transpose(1, 2).reshape(
                    patch_tokens.size(0),
                    patch_tokens.size(2),
                    spatial_dim,
                    spatial_dim,
                )
            else:
                feature_map = None
            return embedding, feature_map

        feature_map = self.features(x)
        feature_map = self.context_module(feature_map)
        pooled = self.pool(feature_map).flatten(1)
        pooled = self.norm(pooled)
        if self.fusion_head is not None:
            pooled = self.fusion_head(pooled, feature_map)
        if self.feature_adapter is not None:
            pooled = self.feature_adapter(pooled)
        return pooled, feature_map

    def compute_training_logits(self, classifier_input, labels=None):
        if self.use_amcc and labels is not None:
            return self.classifier.forward_with_margin(classifier_input, labels)
        return self.classifier(classifier_input)

    def set_class_prototypes(self, prototypes, counts=None) -> None:
        if hasattr(self.classifier, "set_prototypes"):
            self.classifier.set_prototypes(prototypes, counts)

    def clear_class_prototypes(self) -> None:
        if self.center_memory is not None:
            self.center_memory.clear_centers()
        if hasattr(self.classifier, "clear_prototypes"):
            self.classifier.clear_prototypes()
        if hasattr(self.classifier, "clear_centers"):
            self.classifier.clear_centers()

    def update_class_centers(self, classifier_input, labels, momentum: float = 0.9) -> None:
        if self.center_memory is not None:
            self.center_memory.update_centers(classifier_input, labels, momentum=momentum)
        if hasattr(self.classifier, "update_centers"):
            self.classifier.update_centers(classifier_input, labels, momentum=momentum)

    def prototype_alignment_loss(self, classifier_input, labels):
        if self.center_memory is not None:
            return self.center_memory.alignment_loss(classifier_input, labels)
        if hasattr(self.classifier, "prototype_alignment_loss"):
            return self.classifier.prototype_alignment_loss(classifier_input, labels)
        return classifier_input.new_tensor(0.0)

    def forward(self, x):
        embedding, feature_map = self.forward_features(x)
        classifier_input = self.dropout(embedding)
        logits = self.classifier(classifier_input)
        return {
            "logits": logits,
            "embedding": embedding,
            "feature_map": feature_map,
            "classifier_input": classifier_input,
        }


def build_model(model_config: dict, num_classes: int) -> RSSceneClassifier:
    return RSSceneClassifier(model_config=model_config, num_classes=num_classes)
