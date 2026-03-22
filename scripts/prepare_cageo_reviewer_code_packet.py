from __future__ import annotations

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ROOT = ROOT / "paper" / "submission_ready" / "cageo_reviewer_code_packet"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a lightweight reviewer-facing code packet for the C&G submission."
    )
    parser.add_argument(
        "--output-dir",
        default=str(OUTPUT_ROOT),
        help="Directory where the reviewer code packet will be written.",
    )
    parser.add_argument(
        "--zip",
        action="store_true",
        help="Also create a zip archive next to the output directory.",
    )
    return parser.parse_args()


def copy_path(src: Path, dst: Path) -> None:
    if not src.exists():
        return
    if src.is_dir():
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    else:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


def write_readme(output_dir: Path) -> None:
    content = """# C&G Reviewer Code Packet

This packet provides the minimal code and documentation needed to inspect and reproduce the current `Computers & Geosciences` manuscript workflow without bundling large raw datasets or heavy outputs.

## Included

- `configs/`: experiment configurations
- `scripts/`: training, evaluation, aggregation, and manuscript-build scripts
- `src/`: project source code
- `tests/`: lightweight integrity checks for the C&G workspace
- `docs/`: protocol, results snapshot, reviewer quickstart, and reviewer risk notes
- `paper/generated_lowshot/`: LaTeX tables used by the manuscript
- `LICENSE`: default open-source license prepared for the final public release

## Not Included

- `data/raw/`: public datasets must be downloaded separately
- `outputs/`: heavy checkpoints and logs are intentionally excluded
- final public repository URL: to be filled once the online repository is created

## Quickstart

1. Install dependencies with `D:\\python311\\python.exe -m pip install -r requirements.txt`
2. Prepare public datasets under:
   - `data/raw/AID/<class_name>/*.jpg`
   - `data/raw/NWPU_RESISC45/<class_name>/*.jpg`
3. Read `docs/experiment_protocol.md`
4. Use `docs/reviewer_reproduction_quickstart.md` as the shortest reproduction path
"""
    (output_dir / "README.md").write_text(content, encoding="utf-8")


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir).resolve()
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    copy_path(ROOT / "configs", output_dir / "configs")
    copy_path(ROOT / "scripts", output_dir / "scripts")
    copy_path(ROOT / "src", output_dir / "src")
    copy_path(ROOT / "tests", output_dir / "tests")
    copy_path(ROOT / "requirements.txt", output_dir / "requirements.txt")
    copy_path(ROOT / "README.md", output_dir / "README_project.md")
    copy_path(ROOT / "LICENSE", output_dir / "LICENSE")

    docs_dir = output_dir / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    for doc_name in [
        "experiment_protocol.md",
        "results_snapshot.md",
        "reviewer_risk_register.md",
        "reviewer_reproduction_quickstart.md",
    ]:
        copy_path(ROOT / "docs" / doc_name, docs_dir / doc_name)

    paper_dir = output_dir / "paper"
    paper_dir.mkdir(parents=True, exist_ok=True)
    copy_path(ROOT / "paper" / "generated_lowshot", paper_dir / "generated_lowshot")

    write_readme(output_dir)
    print(f"prepared C&G reviewer code packet under {output_dir}")

    if args.zip:
        archive_base = output_dir.parent / output_dir.name
        archive_path = shutil.make_archive(str(archive_base), "zip", root_dir=output_dir.parent, base_dir=output_dir.name)
        print(f"packed C&G reviewer code packet zip at {archive_path}")


if __name__ == "__main__":
    main()
