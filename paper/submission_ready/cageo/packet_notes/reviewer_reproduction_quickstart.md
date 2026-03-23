# Reviewer Reproduction Quickstart for C&G

这份说明面向 `Computers & Geosciences` 审稿或内部复核，目标是最短路径复现当前主稿最核心的结果链。

## Workspace Rule

- 从 `D:\codex\treatise\paper_q2_cageo` 根目录执行命令
- 所有新生成结果默认写入当前工作区自己的 `outputs/`
- 不需要也不应该把结果写回旧论文目录

## Public Repository

- Public code repository: `https://github.com/2446099877/paper_q2_cageo`
- Public license: `MIT`

## Environment

- Python: `D:\python311\python.exe`
- Main framework: `PyTorch 2.5.1+cu121`
- Recommended GPU: `RTX 4060 Ti 8GB` or equivalent

## Required Public Data

- `data/raw/AID/<class_name>/*.jpg`
- `data/raw/NWPU_RESISC45/<class_name>/*.jpg`
- 仓库不再分发原始图像，只保留 split manifests 与复现脚本
- 请从各数据集官方来源自行获取原始数据，并按上述目录放置

## Verify Dataset Layout

```bat
D:\python311\python.exe scripts\check_dataset.py --root data\raw\AID --name AID --output outputs\dataset_checks
D:\python311\python.exe scripts\check_dataset.py --root data\raw\NWPU_RESISC45 --name NWPU_RESISC45 --output outputs\dataset_checks
```

## Reproduce Main Results

```bat
D:\python311\python.exe scripts\run_multiseed.py --config configs\experiments\aid_low20_baseline.yaml
D:\python311\python.exe scripts\run_multiseed.py --config configs\experiments\nwpu_low20_baseline.yaml
D:\python311\python.exe scripts\run_multiseed.py --config configs\experiments\aid_low20_dino_base_adapter_ft1_gcfix.yaml
D:\python311\python.exe scripts\run_multiseed.py --config configs\experiments\nwpu_low20_dino_base_adapter_ft1_gcfix.yaml
```

## Aggregate Results

```bat
D:\python311\python.exe scripts\aggregate_results.py --input outputs\aid_low20_convnext_tiny\baseline
D:\python311\python.exe scripts\aggregate_results.py --input outputs\nwpu_low20_convnext_tiny\baseline
D:\python311\python.exe scripts\aggregate_results.py --input outputs\aid_low20_dinov2_base\adapter_ft1_gcfix
D:\python311\python.exe scripts\aggregate_results.py --input outputs\nwpu_low20_dinov2_base\adapter_ft1_gcfix
```

## Refresh Manuscript Tables

```bat
D:\python311\python.exe scripts\refresh_paper_assets.py
```

## Expected Main Direction

- `AID-low20`: proposed workflow should show a clear OA increase over the matched-split `ConvNeXt-Tiny` reference, around `+0.023`
- `NWPU-low20`: proposed workflow should show a modest positive OA shift over the matched-split `ConvNeXt-Tiny` reference, around `+0.007`
- `NWPU-low20` 的三-seed 结果应按“directional matched-protocol evidence”解读，而不是 formal significance claim

## Main Artifacts

- Results snapshot: [results_snapshot.md](results_snapshot.md)
- Single-file C&G manuscript: [treatise_cageo_submission.tex](../paper/cageo_template/CAGEO_LaTeXTemplate-main/treatise_cageo_submission.tex)
- Submission-ready packet: [submission_ready/cageo](../paper/submission_ready/cageo)
