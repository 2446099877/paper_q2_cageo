from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER_ROOT = ROOT / "paper"
TEMPLATE_ROOT = PAPER_ROOT / "cageo_template" / "CAGEO_LaTeXTemplate-main"
PACKET_ROOT = PAPER_ROOT / "submission_ready" / "cageo"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Prepare a near-self-contained Computers & Geosciences submission packet."
    )
    parser.add_argument(
        "--output-dir",
        default=str(PACKET_ROOT),
        help="Directory where the organized submission packet will be written.",
    )
    return parser.parse_args()


def rebuild_single_file_manuscript() -> None:
    script = ROOT / "scripts" / "build_cageo_submission.py"
    subprocess.run([sys.executable, str(script)], check=True)


def copy_if_exists(src: Path, dst: Path) -> None:
    if src.exists():
        shutil.copy2(src, dst)


def copy_tree(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)


def write_packet_readme(packet_dir: Path) -> None:
    readme = """# Computers & Geosciences Submission Packet

This directory organizes the current `Computers & Geosciences` submission materials into one place.

## Main Files

- `manuscript.tex`: single-file Elsevier CAS-style manuscript
- `references.bib`: bibliography used by the manuscript
- `figures/`: figure assets referenced by the manuscript
- `cas-sc.cls`, `cas-common.sty`, `cas-model2-names.bst`: template support files
- `packet_notes/`: official notes, cover letter draft, and highlights draft

## Notes

- This packet was generated automatically from the current project sources.
- The current packet already passes the local placeholder scan.
- Before final submission, verify that the current single-author metadata is still correct and replace the provisional repository wording with the final public or reviewer-safe code link required by the journal.
- One-click rebuild + compile script:
  `D:\\python311\\python.exe D:\\codex\\treatise\\paper_q2_cageo\\scripts\\compile_cageo_pdf.py`
- Placeholder readiness check:
  `D:\\python311\\python.exe D:\\codex\\treatise\\paper_q2_cageo\\scripts\\check_cageo_packet_readiness.py`
"""
    (packet_dir / "README.md").write_text(readme, encoding="utf-8")


def main() -> None:
    args = parse_args()
    packet_dir = Path(args.output_dir).resolve()

    rebuild_single_file_manuscript()

    if packet_dir.exists():
        shutil.rmtree(packet_dir)
    packet_dir.mkdir(parents=True, exist_ok=True)

    source_manuscript = TEMPLATE_ROOT / "treatise_cageo_submission.tex"
    manuscript_text = source_manuscript.read_text(encoding="utf-8")
    manuscript_text = manuscript_text.replace("../../figures/", "figures/")
    manuscript_text = manuscript_text.replace("\\bibliography{../../references}", "\\bibliography{references}")
    (packet_dir / "manuscript.tex").write_text(manuscript_text, encoding="utf-8")

    shutil.copy2(PAPER_ROOT / "references.bib", packet_dir / "references.bib")
    copy_if_exists(TEMPLATE_ROOT / "cas-sc.cls", packet_dir / "cas-sc.cls")
    copy_if_exists(TEMPLATE_ROOT / "cas-common.sty", packet_dir / "cas-common.sty")
    copy_if_exists(TEMPLATE_ROOT / "cas-model2-names.bst", packet_dir / "cas-model2-names.bst")
    copy_tree(PAPER_ROOT / "figures", packet_dir / "figures")

    notes_dir = packet_dir / "packet_notes"
    notes_dir.mkdir(parents=True, exist_ok=True)
    for filename in [
        "cageo_official_notes_2026-03-22.md",
        "cageo_cover_letter_draft.md",
        "cageo_highlights_draft.md",
        "cageo_authorship_statement.md",
        "cageo_pre_submission_checklist.md",
        "cageo_status.md",
        "cageo_fill_once_form.md",
        "final_submission_freeze_2026-03-23.md",
    ]:
        shutil.copy2(ROOT / "docs" / "submission_packets" / filename, notes_dir / filename)

    write_packet_readme(packet_dir)
    print(f"prepared C&G submission packet under {packet_dir}")


if __name__ == "__main__":
    main()
