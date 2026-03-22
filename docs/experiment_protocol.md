# Experiment Protocol for C&G

更新时间：`2026-03-22`

## 任务定义

- 任务：`scarce-label remote sensing scene classification`
- 目标定位：`reproducible geocomputing workflow`
- 主数据集：
  - `AID-low20`
  - `NWPU-low20`
- 公平基线：`ConvNeXt-Tiny`
- 主方法：`DINOv2-Base + residual adapter + selective finetuning + feature-center regularization`

## 固定划分协议

- 每个数据集都采用：
  - `20` 张/类训练
  - `10` 张/类验证
  - 其余样本测试
- 固定随机种子：
  - `3407`
  - `3408`
  - `3409`
- 同一 seed 下，所有方法共用同一份 class-balanced split manifest

## 训练设置

- 输入尺寸：`224 x 224`
- 优化器：`AdamW`
- 学习率调度：`CosineAnnealingLR`
- mixed precision：启用
- early stopping：启用
- `DINOv2-Base` 主方法采用：
  - 仅解冻最后一个 transformer block
  - 解冻 final normalization
  - residual adapter
  - feature-center regularization
  - gradient checkpointing
  - gradient accumulation

## 主结果必须报告

- `OA`
- `AA`
- `Kappa`
- 三 seed 均值与标准差
- 总参数量
- 可训练参数量
- `FLOPs`
- confusion matrix
- gradient-based activation 可视化

## 当前默认口径

- 不把稿件包装成“遥感专用结构创新”
- 不把稿件包装成“轻量部署模型”
- 主卖点固定为：
  - `public data`
  - `fixed manifests`
  - `multi-seed aggregation`
  - `scripted evidence regeneration`
  - `8 GB GPU feasible adaptive transfer`
