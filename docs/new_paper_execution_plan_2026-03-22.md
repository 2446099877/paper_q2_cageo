# New Paper Execution Plan

更新时间：`2026-03-22`

## 结论

这次新论文我已经直接选定为：

- 目标期刊：`Computers & Geosciences`
- 论文方向：`reproducible geocomputing workflow for scarce-label remote sensing scene classification`
- 资产底座：复用现有 `AID-low20 + NWPU-low20 + DINOv2-Base + ConvNeXt-Tiny` 主结果、消融、复杂度和图表

## 为什么不是继续按旧 `MVA` 走

- 公开可访问的 `2025` 分区资料已经不足以支持 `MVA` 仍是默认二区。
- 这次用户约束是“必须二区”，因此不能继续押一个公开口径已经显著变差的目标。

## 为什么不是直接做“更独立的第二篇系统比较稿”

并行勘察结果表明，如果只看“和当前主稿的区分度”，最强切口其实是：

- `ConvNeXt-Tiny vs DINOv2-S vs DINOv2-B`
- `linear / mean / adapter-only / partial-FT`
- 做成一篇“backbone 容量与适配策略系统比较”稿

但这条路线当前没有被选为默认执行方案，原因很现实：

1. `DINOv2-small` 目前大多还是单 seed 结果
2. 如果要把它打到投稿强度，需要补三 seed 和统一聚合
3. `NWPU` 上的差距本来就不大，系统比较稿对统计证据要求更高
4. 当前最接近完成态、最容易尽快形成真正二区投稿包的，仍然是现有 `DINOv2-Base` 主线的 geocomputation 重写版

所以本次采用的是：

- 先用现有最成熟资产快速形成 `C&G` 新稿支线
- 已经把 `DINOv2-small` 的关键三 seed 补齐，用结果反证它更适合作为补充比较线
- 后续如果时间和算力允许，再决定是否把系统比较并入扩展实验或另起第二篇

## 当前已经完成的动作

### 选刊与资料

- 新增 `docs/journal_revalidation_2026-03-22.md`
- 新增 `docs/submission_packets/cageo_official_notes_2026-03-22.md`
- 新增 `cageo` 版 cover letter 与 highlights 草稿

### 稿件支线

- 新增 `paper/sections_cageo/`
  - `abstract.tex`
  - `introduction.tex`
  - `related_work.tex`
  - `conclusion.tex`

### 构建与打包

- 新增 `scripts/build_cageo_submission.py`
- 新增 `scripts/prepare_cageo_packet.py`
- 下载官方 `C&G` LaTeX 模板到：
  - `paper/cageo_template/CAGEO_LaTeXTemplate-main`
- 已生成：
  - `paper/cageo_template/CAGEO_LaTeXTemplate-main/treatise_cageo_submission.tex`
  - `paper/submission_ready/cageo/manuscript.tex`
  - `paper/submission_ready/cageo/manuscript.pdf`
- 已完成第二轮质量收束：
  - `related_work` 更强调 `rebuildable geocomputing evidence`
  - `experiments` 明确写入 `manifest-to-result` 可追溯与脚本化聚合
  - `cover letter / highlights` 已改成更贴近 `C&G` 编辑视角的口径
- 已完成公开仓库落地：
  - `https://github.com/2446099877/paper_q2_cageo`
  - `CITATION.cff`、`Code availability`、cover letter 已切到真实公开仓库地址

### 新工作区内已新增实验

- 已在独立工作区中补齐 `AID low20 + DINOv2-small + adapter_ft2` 的 `3408 / 3409`
- 当前三 seed 聚合为：
  - `0.9262 ± 0.0020`
- 相对 `ConvNeXt-Tiny` 基线：
  - `+0.0082 OA`
- 也已补齐 `NWPU low20 + DINOv2-small + adapter_ft2` 的 `3408 / 3409`
- 当前三 seed 聚合为：
  - `0.8649 ± 0.0097`
- 相对 `ConvNeXt-Tiny` 基线：
  - `-0.0071 OA`
- 记录见：
  - [experiment_update_2026-03-22_dinov2_small.md](/D:/codex/treatise/paper_q2_cageo/docs/experiment_update_2026-03-22_dinov2_small.md)

## 当前新稿的定位

### 主卖点

- 公共数据
- 固定 split manifests
- 多随机种子
- 开源可复现
- 8GB GPU 可训练
- 强 pretrained backbone 的受控适配

### 不主打的点

- 不是轻量推理模型
- 不是遥感专用结构大创新
- 不是极大幅度跨数据集提升

## 接下来最值钱的工作顺序

1. 继续把 `C&G` 稿件中的作者信息、仓库链接和 code availability 补全
2. 对摘要、引言、相关工作做一轮更强的 geocomputation 化润色
3. 检查 `C&G` 稿件是否需要进一步压缩 cover letter 和 highlights 的措辞
4. 如果要增强与旧稿的区分度，优先整理：
   - `DINOv2-small` 已完成的 `AID/NWPU` 三 seed 正负结果
   - 再决定是作为附录扩展，还是保留成第二篇系统比较稿的种子资产

## 当前决定

本轮默认不再等待新的人工拍板：

- `C&G` 新稿作为当前主执行线
- `MVA` 旧包仅保留为历史资产
- `DINOv2-small` 不升级为当前主稿核心卖点
- “系统比较第二篇”作为下一优先级备选，不阻塞当前二区路线
