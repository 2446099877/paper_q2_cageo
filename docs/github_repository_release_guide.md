# GitHub Repository Release Guide

这份说明面向当前第二篇 `Computers & Geosciences` 投稿线，目标是尽快建立一个干净、可引用、可公开的 GitHub 仓库。

## 推荐结论

- 不要直接把整个 `D:\codex\treatise` 上传到 GitHub
- 只发布 `D:\codex\treatise\paper_q2_cageo` 这一套独立工作区
- 仓库建议公开为 `public`
- 建仓时不要让 GitHub 自动生成新的 `README`、`LICENSE` 或 `.gitignore`

## 推荐仓库名

优先推荐：

- `reproducible-rssc-dinov2`

可替代：

- `scarce-label-rssc-workflow`
- `dinov2-geocomputing-rssc`

## 推荐仓库描述

`Reproducible geocomputing workflow for scarce-label remote sensing scene classification on AID and NWPU-RESISC45.`

## GitHub 网页端要怎么点

1. 登录 GitHub
2. 点右上角 `New repository`
3. Repository name 填：`reproducible-rssc-dinov2`
4. Description 填上面的推荐描述
5. 选择 `Public`
6. 不勾选：
   - `Add a README file`
   - `Add .gitignore`
   - `Choose a license`
7. 点 `Create repository`

## 本地最优发布方式

在 `D:\codex\treatise\paper_q2_cageo` 目录执行：

```bat
git init
git branch -M main
git add .
git commit -m "Initial public release for C&G submission"
git remote add origin https://github.com/<your-account>/reproducible-rssc-dinov2.git
git push -u origin main
```

如果远端已经有内容，先执行：

```bat
git pull origin main --allow-unrelated-histories
```

再处理冲突后继续 push。

## 发布前必须确认的内容

- 顶层 `README.md` 是给编辑和审稿人看的，不是内部中文工作说明
- `LICENSE` 已存在，当前是 `MIT`
- `CITATION.cff` 已存在，但需要把 `repository-code` 改成真实 GitHub URL
- `outputs/` 下的大模型权重、checkpoint、压缩包不应上传
- 原始公开数据不上传
- 第一篇论文目录和资产不上传

## 建完仓库后立刻要做的事

1. 复制真实仓库地址
2. 回到本地，把以下位置里的占位仓库地址补成真实 URL：
   - `CITATION.cff`
   - `paper/submission_ready/cageo/manuscript.tex` 对应的源生成逻辑
   - `scripts/build_cageo_submission.py` 里的 `Code availability` 相关表述
3. 重新运行：

```bat
python scripts\compile_cageo_pdf.py
python scripts\check_cageo_packet_readiness.py
python -m unittest discover -s tests
```

## GitHub 页面建议补充

- Topics 可加：
  - `remote-sensing`
  - `geocomputing`
  - `reproducibility`
  - `dinov2`
  - `scene-classification`
  - `pytorch`
- 建议在仓库首页保留：
  - README
  - LICENSE
  - CITATION
  - main branch

## 当前最重要提醒

仓库一旦建好，把真实 GitHub URL 发给我。我下一步就可以直接把论文里的 `Code availability`、投稿包和引用元数据全部改成最终可投版本。
