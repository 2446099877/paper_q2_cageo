# Reproducible Selective Adaptation of DINOv2 for Scarce-Label Remote Sensing Scene Classification

This repository contains the independent workspace for the second paper targeting `Computers & Geosciences`. It is organized as a reproducible geocomputing workflow for scarce-label remote sensing scene classification rather than as a remote-sensing-specific architecture release.

## Scope

- Public benchmarks: `AID` and `NWPU-RESISC45`
- Fixed protocol: `20` training images and `10` validation images per class
- Main baseline: `ConvNeXt-Tiny`
- Main workflow: `DINOv2-Base + selective finetuning + residual adapter + feature-center regularization`
- Positioning: `public data + fixed split manifests + multi-seed aggregation + rebuildable manuscript evidence`

## Repository Layout

- `configs/`: experiment configurations
- `data/splits/`: fixed split manifests used by the paper
- `docs/`: execution notes, result snapshots, reviewer quickstart, and submission materials
- `outputs/`: workspace-local result artifacts for the second paper only
- `paper/`: LaTeX sources, figures, generated tables, and submission-ready packet
- `scripts/`: experiment, aggregation, and manuscript build scripts
- `src/`: source modules copied into the independent workspace
- `tests/`: local guardrail tests for release and submission assets

## Public Data

Raw datasets are not redistributed in this repository. Download them separately and place them under your own data root:

- `AID`
- `NWPU-RESISC45`

The project keeps fixed split manifests under `data/splits/` so that all compared methods can be evaluated on identical class-balanced partitions.

## Environment

- Python: `3.11`
- Main framework: `PyTorch 2.5.1+cu121`
- Recommended GPU for the main DINOv2 workflow: `RTX 4060 Ti 8GB` or equivalent

Install the main dependencies with:

```bat
pip install -r requirements.txt
```

## Quick Start

Check public dataset layout:

```bat
python scripts\check_dataset.py --root ..\data\raw\AID --name AID --output outputs\dataset_checks
python scripts\check_dataset.py --root ..\data\raw\NWPU_RESISC45 --name NWPU_RESISC45 --output outputs\dataset_checks
```

Run the main multi-seed experiments:

```bat
python scripts\run_multiseed.py --config configs\experiments\aid_low20_baseline.yaml
python scripts\run_multiseed.py --config configs\experiments\nwpu_low20_baseline.yaml
python scripts\run_multiseed.py --config configs\experiments\aid_low20_dino_base_adapter_ft1_gcfix.yaml
python scripts\run_multiseed.py --config configs\experiments\nwpu_low20_dino_base_adapter_ft1_gcfix.yaml
```

Aggregate results:

```bat
python scripts\aggregate_results.py --input outputs\aid_low20_convnext_tiny\baseline
python scripts\aggregate_results.py --input outputs\nwpu_low20_convnext_tiny\baseline
python scripts\aggregate_results.py --input outputs\aid_low20_dinov2_base\adapter_ft1_gcfix
python scripts\aggregate_results.py --input outputs\nwpu_low20_dinov2_base\adapter_ft1_gcfix
```

Rebuild the manuscript assets and compile the `Computers & Geosciences` submission PDF:

```bat
python scripts\compile_cageo_pdf.py
```

Check packet readiness:

```bat
python scripts\check_cageo_packet_readiness.py
```

Prepare the reviewer-safe code packet:

```bat
python scripts\prepare_cageo_reviewer_code_packet.py --zip
```

## Reproducibility Notes

- All methods use the same seed-controlled split manifests for a given seed.
- Main comparisons are reported as three-seed mean and standard deviation.
- The manuscript tables are rebuilt from recorded outputs rather than manual transcription.
- New artifacts for this paper are intended to stay within this workspace and not pollute the first paper.

## Main Documentation

- Results snapshot: [docs/results_snapshot.md](docs/results_snapshot.md)
- Reviewer quickstart: [docs/reviewer_reproduction_quickstart.md](docs/reviewer_reproduction_quickstart.md)
- Submission status: [docs/submission_packets/cageo_status.md](docs/submission_packets/cageo_status.md)
- GitHub release guide: [docs/github_repository_release_guide.md](docs/github_repository_release_guide.md)

## License

This project is prepared for public release under the `MIT License`. See [LICENSE](LICENSE).
