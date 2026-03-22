# Journal Revalidation for the New Q2 Route

更新时间：`2026-03-22`

## 结论

- 新论文默认目标期刊改为 `Computers & Geosciences`。
- 旧的 `Machine Vision and Applications` 不再作为默认二区目标。
- 当前最优策略不是继续沿用旧 shortlist，而是把稿件口径改成 `geocomputation + reproducibility + scarce-label remote sensing`。

## 这次为什么要重验

仓库里此前的默认首投路线是 `Machine Vision and Applications (MVA)`，但这份判断形成于 `2026-03-18` 前后，依赖的是当时的公开二手信息。`2026-03-22` 重新核验后，公开可访问资料已经不足以继续支持“默认二区首投仍然是 MVA”的判断。

## 本次核验到的公开信息

### 1. `Computers & Geosciences`

- `2025-02-26` 发布的湖南大学图书馆期刊分区 PDF 仍把 `Computers & Geosciences` 列为 `中科院 2区`。
- 期刊官方主页明确覆盖：
  - `computer methods`
  - `remote sensing`
  - `image analysis`
  - `algorithms and software`
- 官方投稿指南明确要求稿件必须包含 `Code availability section`，并且未开源代码的稿件会被系统性退稿；这和当前仓库“代码、配置、split manifest、表格重建脚本齐全”的资产状态高度一致。

### 2. `Machine Vision and Applications`

- `2025-03-20` 发布的武汉大学图书馆期刊分区页面把 `Machine Vision and Applications` 标为 `中科院 4区`。
- `2025-03-17` 发布的湖南大学图书馆期刊分区 PDF 也把 `Machine Vision and Applications` 列为 `4区`。
- 这意味着继续把 `MVA` 当作“稳妥二区路线”风险过高，即使 scope 仍然匹配，也不再满足“这次必须二区”的硬约束。

## 为什么这次选 `Computers & Geosciences`

### 优点

- `二区` 公开口径目前仍然成立。
- `remote sensing + algorithms + software + reproducibility` 的 scope 和当前资产贴合。
- 默认订阅制，可避开高 APC 压力。
- 官方鼓励代码可得性，正好能把当前仓库的复现实验链转成稿件卖点。

### 相比旧稿需要同步调整的口径

- 不再把稿件包装成纯视觉期刊的“parameter-efficient vision model paper”。
- 要把重点改成：
  - `scarce-label geospatial image analysis`
  - `reproducible protocol`
  - `open-source implementation`
  - `commodity-GPU feasibility`
- 结论表述要更克制，避免写成“通用视觉 SOTA 改进”。

## 新论文定位

建议的新题目方向：

`Reproducible Selective Adaptation of DINOv2 for Scarce-Label Remote Sensing Scene Classification`

建议的关键词：

- `remote sensing scene classification`
- `scarce-label learning`
- `reproducibility`
- `DINOv2`
- `transfer learning`
- `geocomputation`

## 与现有 MVA 成稿的关系

- 旧的 `MVA` 投稿包保留，不删除。
- 新分支不是简单换封面，而是换投稿叙事：
  - 旧稿强调 `parameter-efficient adaptation`
  - 新稿强调 `reproducible geocomputing workflow under scarce labels`
- 方法主体仍可复用现有 `AID + NWPU + DINOv2-Base` 实验资产，这是当前性价比最高的做法。

## 当前执行决定

从本文件起，仓库里的“新论文”默认指向：

1. 目标期刊：`Computers & Geosciences`
2. 论文定位：`Q2 geocomputation`
3. 资产底座：复用现有 `AID-low20 + NWPU-low20`、多 seed 结果、复杂度统计、图表和脚本
4. 文稿策略：新开 `C&G` 支线，不覆盖旧 `MVA` 包
