# Results Snapshot for C&G

更新时间：`2026-03-23`

## 主线结果

### AID-low20

- `ConvNeXt-Tiny`: `0.9179 ± 0.0086`
- `DINOv2-Base + Adapter + FT + Center`: `0.9413 ± 0.0036`
- `ΔOA = +0.0234`

### NWPU-low20

- `ConvNeXt-Tiny`: `0.8721 ± 0.0116`
- `DINOv2-Base + Adapter + FT + Center`: `0.8790 ± 0.0085`
- `ΔOA = +0.0069`
- 当前解释：`modest but positive shift under the fixed protocol`, interpreted as directional evidence rather than a formal significance claim

## 关键消融

### NoAdapter

- `AID-low20`: `0.9416 ± 0.0066`
- `NWPU-low20`: `0.8793 ± 0.0112`
- 当前解释：均值与 full 接近，但 seed 波动更大

### NoCenter

- `AID-low20`: `0.9350 ± 0.0075`
- `NWPU-low20`: `0.8722 ± 0.0056`
- 当前解释：`AID` 上均值下降更明确，`NWPU` 上是较小但同方向的正向差异，支持保留 center regularization

### DINOv2-small + adapter_ft2

- `AID-low20`: `0.9262 ± 0.0020`
- `NWPU-low20`: `0.8649 ± 0.0097`
- 当前解释：
  - `AID` 上有正增益
  - `NWPU` 上相对 `ConvNeXt-Tiny` 为 `-0.0071 OA`
  - 因此这条线只保留为补充比较证据，不升格为当前主稿核心卖点

## 复杂度

- `ConvNeXt-Tiny`: `27.8M total`, `27.8M trainable`, `8.93G FLOPs`
- `DINOv2-Base + NoAdapter + FT`: `86.6M total`, `7.12M trainable`, `43.93G FLOPs`
- `DINOv2-Base + Adapter + FT`: `87.0M total`, `7.51M trainable`, `43.93G FLOPs`

## 当前最稳结论

1. `DINOv2-Base + selective finetuning` 是当前主提升来源。
2. residual adapter 的价值更接近稳定性增强，而不是主要均值来源。
3. center regularization 在当前双数据集三 seed 口径下主要带来均值收益，因此仍值得保留。
4. 第二篇正文应继续坚持 `reproducible workflow` 叙事，而不是扩展成 backbone capacity 比较论文。
