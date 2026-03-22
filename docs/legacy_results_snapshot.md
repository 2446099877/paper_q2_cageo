# Results Snapshot

更新时间：`2026-03-19`

## 当前主线

- 任务：`low-shot remote sensing scene classification`
- 数据集：`AID-low20 + NWPU-low20`
- 公平基线：`ConvNeXt-Tiny`
- 主方法：`DINOv2-Base + Residual Adapter + partial finetune(last-1 block) + feature-center regularization`

## 主结果

### AID-low20

- Baseline: `0.9179 ± 0.0086`
- Full method: `0.9413 ± 0.0036`
- 增益：`+0.0234`

### NWPU-low20

- Baseline: `0.8721 ± 0.0116`
- Full method: `0.8790 ± 0.0085`
- 增益：`+0.0069`

## 关键消融

### NoAdapter

#### AID-low20

- `0.9416 ± 0.0066`
- 相对 full：均值几乎持平，波动更大

#### NWPU-low20

- `0.8793 ± 0.0112`
- 相对 full：均值几乎持平，波动更大

### NoCenter

#### AID-low20

- `0.9350 ± 0.0075`
- 相对 full：均值更低，波动更大

#### NWPU-low20

- `0.8722 ± 0.0056`
- 相对 full：均值更低，波动更小

### AdapterOnly

#### 三 seed 最终结果

- `AID-low20`：`0.8981 ± 0.0050`
- `NWPU-low20`：`0.7782 ± 0.0369`
- 当前解释：`adapter-only` 在两个数据集都显著低于 full method，且 `NWPU` 波动明显更大，进一步支持“partial finetune 是核心收益来源”。

## 当前最稳结论

1. `DINOv2-Base + partial finetune` 是当前性能提升的核心来源。
2. `adapter` 的主要作用更接近稳定性增强，而不是均值大幅提升。
3. `feature-center regularization` 现在已经不再是 mixed signal：
   - 在 `AID` 和 `NWPU` 上都优于对应的 `no-center` 三 seed 结果。
4. `adapter-only` 已在 `AID + NWPU` 两个数据集完成三 seed 收口，并且都明显弱于 full method。

## 复杂度

- `ConvNeXt-Tiny`: `27.8M params`, `27.8M trainable`, `8.93G FLOPs`
- `DINOv2-Base+NoAdapter+FT`: `86.6M params`, `7.12M trainable`, `43.93G FLOPs`
- `DINOv2-Base+Adapter+FT`: `87.0M params`, `7.51M trainable`, `43.93G FLOPs`

## 可直接引用的论文资产

- 主结果表：[main_results.tex](/D:/codex/treatise/paper/generated_lowshot/main_results.tex)
- 消融表：[ablation_results.tex](/D:/codex/treatise/paper/generated_lowshot/ablation_results.tex)
- 稳定性表：[stability_results.tex](/D:/codex/treatise/paper/generated_lowshot/stability_results.tex)
- seed-wise 表：[seedwise_results.tex](/D:/codex/treatise/paper/generated_lowshot/seedwise_results.tex)
- 复杂度表：[complexity_results.tex](/D:/codex/treatise/paper/generated_lowshot/complexity_results.tex)

## 当前默认叙事

- `strong representation transfer`
- `parameter-efficient adaptation`
- `cross-dataset stability`
