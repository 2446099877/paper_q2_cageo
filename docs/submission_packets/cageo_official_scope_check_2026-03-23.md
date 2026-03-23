# C&G Official Scope Check (2026-03-23)

更新时间：`2026-03-23`

## Official Source

- Source page: `https://shop.elsevier.com/journals/computers-and-geosciences/0098-3004`
- 核对时间：`2026-03-23`

## Current Journal-Side Signals

- `Computers & Geosciences` 明确要求论文处于 `Computer Sciences` 与 `Geosciences` 交叉处。
- 期刊优先接受：
  - geoscience 问题上的 `computational / informatics` 创新
  - remote sensing data analysis, AI, software engineering, data processing 等计算要素
- 期刊明确不欢迎：
  - 没有显著计算机科学创新的纯地学稿件
  - 没有清晰地学应用的纯计算机科学稿件
  - 只是标准实现、标准 GIS 用法、标准 GUI 的稿件
- 对代码稿的当前硬要求：
  - 代码需要可下载
  - 仓库链接需要写进稿件
  - 开源许可证需要在稿件中明确标出
  - 非开源代码稿件会被 desk reject

## Current Manuscript Alignment

- 当前主稿已经避免把自己写成“遥感结构创新论文”：
  - 重点落在 `reproducible workflow`、`fixed manifests`、`multi-seed aggregation`、`auditable evidence generation`
- 当前主稿也避免把自己写成“纯计算机视觉 benchmark”：
  - 明确绑定 public remote sensing benchmarks 与 geospatial image analysis use case
- 当前稿件满足当前代码开放要求：
  - 正文已写公开仓库
  - 正文已写 `MIT`
  - reviewer-safe zip 已单独准备

## Remaining Scope-Side Discipline

- 不要把主卖点改回“DINOv2 比 ConvNeXt 强很多”。
- 不要把稿件扩成“backbone capacity comparison paper”。
- 不要把 `NWPU` 小增益写成跨数据集强结论。
- 后续所有修改都继续优先强化：
  - `workflow contribution`
  - `auditable code and data handling`
  - `geocomputing relevance`
  - `reproducibility over one-off accuracy`

## Decision

- 当前 `Computers & Geosciences` 方向保持不变。
- 继续按 `reproducible geocomputing workflow on public remote sensing data` 这条主线推进，是当前最优策略。
