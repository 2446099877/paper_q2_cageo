# Figure Staging Area

这个目录用于放最终投稿稿件会直接引用的图片文件。

## 当前已落盘文件

### Confusion matrices

1. `aid_low20_baseline_confusion.png`
   - 来源：`outputs/aid_low20_convnext_tiny/baseline/seed_3407/test_confusion_matrix.png`
2. `aid_low20_full_confusion.png`
   - 来源：`outputs/aid_low20_dinov2_base/adapter_ft1_gcfix/seed_3407/test_confusion_matrix.png`
3. `nwpu_low20_baseline_confusion.png`
   - 来源：`outputs/nwpu_low20_convnext_tiny/baseline/seed_3407/test_confusion_matrix.png`
4. `nwpu_low20_full_confusion.png`
   - 来源：`outputs/nwpu_low20_dinov2_base/adapter_ft1_gcfix/seed_3407/test_confusion_matrix.png`

### Gradient-based activation visualizations

1. `aid_low20_baseline_activation.png`
   - 来源：`outputs/aid_low20_convnext_tiny/baseline/seed_3407/test_gradcam.png`
2. `aid_low20_full_activation.png`
   - 来源：`outputs/aid_low20_dinov2_base/adapter_ft1_gcfix/seed_3407/test_gradcam.png`
3. `nwpu_low20_baseline_activation.png`
   - 来源：`outputs/nwpu_low20_convnext_tiny/baseline/seed_3407/test_gradcam.png`
4. `nwpu_low20_full_activation.png`
   - 来源：`outputs/nwpu_low20_dinov2_base/adapter_ft1_gcfix/seed_3407/test_gradcam.png`

## 使用原则

- 优先选择与正文主表一致的代表性 seed；当前统一使用 `seed_3407`。
- 最终文件名保持语义清楚，不直接把 `seed_3407` 暴露到论文图名里。
- activation 类图片在正文中统一表述为 `gradient-based activation visualization`，避免把 token-backbone 的可解释性结果夸大成严格的 layer-specific Grad-CAM。
- 如果后面补了更合适的代表图，可直接同名替换，不影响正文结构。
