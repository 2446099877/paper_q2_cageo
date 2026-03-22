# Reviewer Risk Register for C&G

更新时间：`2026-03-22`

## 当前稿件快照

- 目标期刊：`Computers & Geosciences`
- 论文定位：`reproducible geocomputing workflow`
- 主数据集：`AID-low20 + NWPU-low20`
- 公平基线：`ConvNeXt-Tiny`
- 主方法：`DINOv2-Base + residual adapter + selective finetuning + feature-center regularization`

## 最高优先级风险

### 1. 审稿人认为方法创新不足

典型攻击：

- “只是强 backbone 的迁移学习。”
- “看起来不像结构创新论文。”

防守口径：

- 主动承认本文不是 architecture-first 论文。
- 明确贡献是：
  - `fixed manifests`
  - `multi-seed aggregation`
  - `scripted evidence regeneration`
  - `8 GB GPU feasible adaptive transfer`

### 2. 审稿人认为 NWPU 增益偏小

典型攻击：

- “第二个数据集提升有限，泛化结论是否过强？”

防守口径：

- 不写“大幅跨数据集领先”。
- 改写为：
  - `AID` 提升明确
  - `NWPU` 提升保守但方向一致
  - 两个公开基准共同支撑 workflow 稳定性

### 3. 审稿人质疑代码可得性

典型攻击：

- “是否真的能复现？”
- “是否只是承诺开源？”

防守口径：

- 提前准备 reviewer-safe code packet
- 明确公开协议：
  - 审稿期提供 reviewer-safe access
  - 正式公开仓库发布时附带 `MIT License`

## 中优先级风险

### 4. 审稿人认为 adapter 不是主要均值来源

应对：

- 诚实承认这一点
- 保持“adapter mainly improves stability”的写法

### 5. 审稿人认为复杂度较高

应对：

- 不再使用“lightweight”口径
- 只强调：
  - trainable subset 小
  - 8GB GPU 可训练

### 6. 审稿人问为什么不用更小 backbone

应对：

- 已完成 `DINOv2-small` 补充实验
- 直接报告它在 `NWPU` 上不稳定，不升格为正文主方法

## 当前总原则

- 这篇稿子的可信度要高于“看起来很新”
- 宁可保守，也不夸大
