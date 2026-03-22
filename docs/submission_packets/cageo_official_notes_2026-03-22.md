# Computers & Geosciences Official Notes

更新时间：`2026-03-22`

## 结论

- 当前新论文的默认目标期刊为 `Computers & Geosciences`。
- 官方模板、官方投稿要求和当前仓库资产是相互兼容的。
- 这条线比继续走 `MVA` 更符合“必须二区”的硬约束。

## 官方要求摘要

根据期刊官方 LaTeX 模板 README 与 Guide for Authors：

- 稿件必须是 `single column` 且 `double spaced`
- 参考文献必须使用 `author-date` 格式
- 必须包含：
  - `Cover letter`
  - `Highlights`
  - `Authorship statement`
  - `Code availability section`
- 官方指南强调：
  - 代码未开源的稿件会被系统性 desk reject

## 与当前仓库的匹配点

### 已满足或接近满足

- 有明确的代码仓库结构
- 有脚本化实验链
- 有固定 split manifests 和多随机种子协议
- 有图表生成脚本与表格重建脚本
- 有 reviewer-safe code packet 思路
- 有可公开的数据来源说明

### 还需要继续收口

- `Code availability` 段落需要替换成最终仓库链接
- `Cover letter` 需要改成 `C&G` 版本
- `Highlights` 需要改成 `C&G` 版本
- 作者贡献和作者信息仍需最终补全

## 官方模板资产

已下载并放入：

- `paper/cageo_template/CAGEO_LaTeXTemplate-main`

当前模板内包含：

- `cas-sc.cls`
- `cas-common.sty`
- `cas-model2-names.bst`
- `main_document.tex`

## 推荐稿件卖点

为了更贴合 `Computers & Geosciences`，摘要和引言建议强调：

1. `scarce-label geospatial image analysis`
2. `reproducible protocol and open-source workflow`
3. `commodity-GPU feasibility`
4. `cross-dataset evidence rather than single-split anecdotal gain`

## 当前决定

从现在开始：

- `C&G` 作为默认新论文出口
- `MVA` 仅保留为旧路线资产，不再作为默认主推
