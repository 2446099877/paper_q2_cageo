# Asset Manifest

## 当前作用

这份文档把“已经具备的可投稿资产”和“还缺的资产”分开，避免后面临近投稿时重复翻目录。

## 已经具备的主结果资产

### AID-low20 baseline

- 目录：`outputs/aid_low20_convnext_tiny/baseline/seed_3407`
- 目录：`outputs/aid_low20_convnext_tiny/baseline/seed_3408`
- 目录：`outputs/aid_low20_convnext_tiny/baseline/seed_3409`
- 已确认存在：
  - `summary.json`
  - `test_summary.json`
  - `test_confusion_matrix.png`
  - `test_gradcam.png`

### AID-low20 full method

- 目录：`outputs/aid_low20_dinov2_base/adapter_ft1_gcfix/seed_3407`
- 目录：`outputs/aid_low20_dinov2_base/adapter_ft1_gcfix/seed_3408`
- 目录：`outputs/aid_low20_dinov2_base/adapter_ft1_gcfix/seed_3409`
- 已确认存在：
  - `summary.json`
  - `test_summary.json`
  - `test_confusion_matrix.png`
  - `test_gradcam.png`

### NWPU-low20 baseline

- 目录：`outputs/nwpu_low20_convnext_tiny/baseline/seed_3407`
- 目录：`outputs/nwpu_low20_convnext_tiny/baseline/seed_3408`
- 目录：`outputs/nwpu_low20_convnext_tiny/baseline/seed_3409`
- 已确认存在：
  - `summary.json`
  - `test_summary.json`
  - `test_confusion_matrix.png`
  - `test_gradcam.png`

### NWPU-low20 full method

- 目录：`outputs/nwpu_low20_dinov2_base/adapter_ft1_gcfix/seed_3407`
- 目录：`outputs/nwpu_low20_dinov2_base/adapter_ft1_gcfix/seed_3408`
- 目录：`outputs/nwpu_low20_dinov2_base/adapter_ft1_gcfix/seed_3409`
- 已确认存在：
  - `summary.json`
  - `test_summary.json`
  - `test_confusion_matrix.png`
  - `test_gradcam.png`

## 已整理到论文目录的正式图片

以下文件已经复制到 [paper/figures](/D:/codex/treatise/paper/figures)，可以直接被 LaTeX 主稿引用：

- `aid_low20_baseline_confusion.png`
- `aid_low20_full_confusion.png`
- `nwpu_low20_baseline_confusion.png`
- `nwpu_low20_full_confusion.png`
- `aid_low20_baseline_activation.png`
- `aid_low20_full_activation.png`
- `nwpu_low20_baseline_activation.png`
- `nwpu_low20_full_activation.png`

说明：

- 这些图片统一使用代表性 `seed_3407` 的测试集结果，不替代正文三 seed 均值结论。
- `activation` 文件名对应的是统一口径的 `gradient-based activation visualization`。
- DINOv2 路线的源文件在运行目录里仍叫 `test_gradcam.png`，但正文不再把它表述为严格的 Grad-CAM。

## 已经具备的关键消融资产

### No-adapter

- `outputs/aid_low20_dinov2_base/ft1_noadapter/seed_3407`
- `outputs/aid_low20_dinov2_base/ft1_noadapter/seed_3408`
- `outputs/aid_low20_dinov2_base/ft1_noadapter/seed_3409`
- `outputs/nwpu_low20_dinov2_base/ft1_noadapter/seed_3407`
- `outputs/nwpu_low20_dinov2_base/ft1_noadapter/seed_3408`
- `outputs/nwpu_low20_dinov2_base/ft1_noadapter/seed_3409`

### No-center

- `outputs/aid_low20_dinov2_base/adapter_ft1_nocenter/seed_3407`
- `outputs/aid_low20_dinov2_base/adapter_ft1_nocenter/seed_3408`
- `outputs/aid_low20_dinov2_base/adapter_ft1_nocenter/seed_3409`
- `outputs/nwpu_low20_dinov2_base/adapter_ft1_nocenter/seed_3407`
- `outputs/nwpu_low20_dinov2_base/adapter_ft1_nocenter/seed_3408`
- `outputs/nwpu_low20_dinov2_base/adapter_ft1_nocenter/seed_3409`

### Adapter-only

- `outputs/aid_low20_dinov2_base/adapter_only/seed_3407`
- `outputs/aid_low20_dinov2_base/adapter_only/seed_3408`
- `outputs/aid_low20_dinov2_base/adapter_only/seed_3409`
- `outputs/nwpu_low20_dinov2_base/adapter_only/seed_3407`
- `outputs/nwpu_low20_dinov2_base/adapter_only/seed_3408`
- `outputs/nwpu_low20_dinov2_base/adapter_only/seed_3409`

## 已经整理进论文的表格

- [main_results.tex](/D:/codex/treatise/paper/generated_lowshot/main_results.tex)
- [ablation_results.tex](/D:/codex/treatise/paper/generated_lowshot/ablation_results.tex)
- [complexity_results.tex](/D:/codex/treatise/paper/generated_lowshot/complexity_results.tex)
- [stability_results.tex](/D:/codex/treatise/paper/generated_lowshot/stability_results.tex)
  - 当前内容：`full / no-adapter / no-center` 的 OA mean/std 对照
- [seedwise_results.tex](/D:/codex/treatise/paper/generated_lowshot/seedwise_results.tex)

## 当前缺口

### 1. 期刊专属附件尚未最终定稿

目前模板已经齐全，但真正投稿前还需要按目标期刊逐项收口：

- cover letter 最终版本
- highlights
- data/code availability statement
- 图文摘要或 graphical abstract（如期刊要求）
- 作者信息与署名单位

## 当前建议

下一轮最值得补的不是再找图，而是继续收紧“投稿级完成度”：

1. 补齐 journal-specific 附件
2. 做一轮主稿排版与术语一致性检查
3. 按目标期刊模板核验投稿字段与必需附件

现在这份资产状态已经从“正文像论文”推进到“正文和关键图表都像论文”。
