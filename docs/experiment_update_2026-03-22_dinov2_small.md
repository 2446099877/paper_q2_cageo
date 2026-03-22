# Experiment Update: DINOv2-Small Cross-Dataset Check

更新时间：`2026-03-22`

## 结论

在新的独立工作区 `paper_q2_cageo` 中，我已经完成 `DINOv2-small + adapter_ft2` 的跨数据集补充核验：

- `AID low20`
- `NWPU low20`
- `DINOv2-small`
- `adapter_ft2`
- 对两个数据集都补齐了 `seed 3408` 和 `seed 3409`

结合从旧资产导入的 `seed 3407`，这条分支现在已经形成完整三 seed 结果。

最终结论不是“这条线全面优于基线”，而是：

- 在 `AID low20` 上，这条线有稳定正增益
- 在 `NWPU low20` 上，这条线没有复现出正增益，反而低于 `ConvNeXt-Tiny`
- 因此 `DINOv2-small` 更适合作为 `capacity / adaptation strategy` 的补充证据，而不应替代当前 `DINOv2-Base` 主线

## AID Low20 三 seed 聚合结果

- `OA = 0.9262 ± 0.0020`
- `AA = 0.9236 ± 0.0008`
- `Kappa = 0.9236 ± 0.0020`

来源文件：

- [aggregated_summary.csv](/D:/codex/treatise/paper_q2_cageo/outputs/aid_low20_dinov2_small/adapter_ft2/aggregated_summary.csv)
- [aggregated_metrics.csv](/D:/codex/treatise/paper_q2_cageo/outputs/aid_low20_dinov2_small/adapter_ft2/aggregated_metrics.csv)

## 与公平基线对比

相对 `ConvNeXt-Tiny` 三 seed 基线：

- baseline: `0.9179 ± 0.0086`
- DINOv2-S + Adapter + FT2: `0.9262 ± 0.0020`
- `ΔOA = +0.0082`

对照表：

- [comparison_table.md](/D:/codex/treatise/paper_q2_cageo/outputs/aid_low20_dinov2_small/adapter_ft2/comparison_vs_baseline/comparison_table.md)

## NWPU Low20 三 seed 聚合结果

- `OA = 0.8649 ± 0.0097`
- `AA = 0.8649 ± 0.0097`
- `Kappa = 0.8618 ± 0.0099`

来源文件：

- [aggregated_summary.csv](/D:/codex/treatise/paper_q2_cageo/outputs/nwpu_low20_dinov2_small/adapter_ft2/aggregated_summary.csv)
- [aggregated_metrics.csv](/D:/codex/treatise/paper_q2_cageo/outputs/nwpu_low20_dinov2_small/adapter_ft2/aggregated_metrics.csv)

## 与公平基线对比：NWPU

相对 `ConvNeXt-Tiny` 三 seed 基线：

- baseline: `0.8721 ± 0.0116`
- DINOv2-S + Adapter + FT2: `0.8649 ± 0.0097`
- `ΔOA = -0.0071`

对照表：

- [comparison_table.md](/D:/codex/treatise/paper_q2_cageo/outputs/nwpu_low20_dinov2_small/adapter_ft2/comparison_vs_baseline/comparison_table.md)

## 当前解释

- 这条 `DINOv2-small` 线在 `AID low20` 上是成立的。
- 但它在 `NWPU low20` 上没有守住正增益，这说明较小 backbone 的收益对数据集更敏感。
- 它仍明显弱于当前主线 `DINOv2-Base`：
  - `DINOv2-Base full`: `0.9413 ± 0.0036`
  - `DINOv2-Small adapter_ft2`: `0.9262 ± 0.0020`
- 因此它更适合作为：
  - `capacity / adaptation strategy` 的系统比较支线
  - 或“较小 backbone 在固定低样本协议下不一定稳定受益”的补充负结果
  - 而不是替代当前 `DINOv2-Base` 主方法

## 对新稿的实际价值

- 这条新增实验已经完成了“是否值得升级为新主线”的验证。
- 结果说明：答案是否定的，当前 `C&G` 稿件继续以 `DINOv2-Base + reproducible workflow` 作为主叙事是更稳的选择。
- 如果后续需要增强与旧稿的区分度，这条线最合适的用途是：
  - 放入补充材料或 rebuttal 资产
  - 说明我们检查过更小 backbone / 不同适配强度，但收益并不跨数据集稳定
  - 反向支持当前主方法选择并非随意挑选单一最好数字

## 下一优先级

1. 不再把 `DINOv2-small` 扩展实验作为当前投稿主阻塞项
2. 优先把这条结果整理成补充证据，避免正文过度扩张
3. 把精力转回：
   - `C&G` 提交包元数据补齐
   - `code availability` 与最终仓库链接
   - 主线 `DINOv2-Base` 结果的 geocomputing 叙事收口

当前已经证明：新工作区不仅能独立编译稿件，也能独立产出新的训练结果，并且可以把新增正负结果都留在本目录内，不污染旧论文资产。
