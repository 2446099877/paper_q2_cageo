# Draft Cover Letter for Computers & Geosciences

Dear Editors,

Please consider our manuscript entitled `Reproducible Selective Adaptation of DINOv2 for Scarce-Label Remote Sensing Scene Classification` for publication in `Computers & Geosciences`.

This manuscript addresses a practical geocomputing problem: remote sensing scene classification when only a small number of labeled images are available per class. Rather than proposing another scene-classification architecture, we contribute a reproducible computational workflow that combines DINOv2-Base selective adaptation, persistent split manifests, scripted multi-seed aggregation, and manuscript-rebuild assets under fixed protocols on two public datasets, AID and NWPU-RESISC45.

The submission is particularly suited to `Computers & Geosciences` for three reasons. First, the work addresses scarce-label geospatial image analysis with public remote sensing benchmarks. Second, the central contribution is a reusable computational workflow rather than architecture-only benchmarking. Third, the code, configuration, and reproduction assets are publicly available at `https://github.com/2446099877/paper_q2_cageo` under the `MIT License`, with a reviewer-safe archive retained for inspection convenience.

Under one fixed class-balanced protocol, we observe a strong overall-accuracy increase on AID from `0.9179` to `0.9413` and a modest positive increase on NWPU-RESISC45 from `0.8721` to `0.8790`, presented as reproducible workflow outcomes rather than universal performance claims. Same-backbone ablations further show that selective finetuning provides the primary gain, while the adapter mainly improves stability and the feature-center regularizer improves mean performance consistency.

To support editorial and reviewer inspection, we have prepared a reviewer-safe code packet containing the split manifests, experiment scripts, configurations, source modules, generated manuscript tables, and reproduction notes. The public repository is already available at `https://github.com/2446099877/paper_q2_cageo`, and the manuscript's `Code availability` section now points to that live release.

This manuscript has not been published previously and is not under consideration elsewhere. The author has approved the manuscript and agrees with its submission to `Computers & Geosciences`.

Sincerely,

Chao Hou
