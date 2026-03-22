# GitHub Repository Release Guide

这份说明记录第二篇 `Computers & Geosciences` 投稿线的公开代码仓库落地结果。

## Current Public Repository

- Public repository: `https://github.com/2446099877/paper_q2_cageo`
- Visibility: `public`
- License: `MIT`

## Current Release Notes

- 只发布了第二篇独立工作区 `D:\codex\treatise\paper_q2_cageo`
- 没有把整个 `D:\codex\treatise` 主仓一起公开
- 原始公开数据没有上传
- `_root_cleanup_archive/` 没有公开
- reviewer-safe zip 包仍保留为单独补充材料，不作为主仓重复副本

## Repository Hygiene Checklist

- 顶层 `README.md` 已改成面向编辑和审稿人的 English-first 说明
- `LICENSE` 已存在并与仓库页面一致
- `CITATION.cff` 已写入真实 GitHub URL
- 仓库可作为论文 `Code availability` 的正式公开落点

## Recommended GitHub Topics

- `remote-sensing`
- `geocomputing`
- `reproducibility`
- `dinov2`
- `scene-classification`
- `pytorch`

## Post-Release Local Actions

仓库上线后，本地仍应继续执行：

```bat
python scripts\compile_cageo_pdf.py
python scripts\check_cageo_packet_readiness.py
python -m unittest discover -s tests
```

## Remaining Manual Checks

- 复查仓库首页 README 展示效果
- 如有需要，在 GitHub 页面补充 topics 和 release
- 正式投稿前再次确认公开仓库中的作者、许可与代码可得性说明一致
