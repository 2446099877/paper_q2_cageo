from __future__ import annotations

import argparse
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAPER_ROOT = ROOT / "paper"
SECTIONS_DIR = PAPER_ROOT / "sections"
GENERATED_DIR = PAPER_ROOT / "generated_lowshot"
TEMPLATE_ROOT = PAPER_ROOT / "cageo_template" / "CAGEO_LaTeXTemplate-main"
OUTPUT_PATH = TEMPLATE_ROOT / "treatise_cageo_submission.tex"
PUBLIC_REPO_URL = "https://github.com/2446099877/paper_q2_cageo"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build a single-file Computers & Geosciences submission manuscript."
    )
    parser.add_argument(
        "--output",
        default=str(OUTPUT_PATH),
        help="Path to the generated single-file LaTeX manuscript.",
    )
    return parser.parse_args()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_environment(text: str, name: str) -> str:
    match = re.search(
        rf"\\begin\{{{name}\}}(.*?)\\end\{{{name}\}}",
        text,
        flags=re.DOTALL,
    )
    if not match:
        raise ValueError(f"Could not extract {name} body")
    return " ".join(match.group(1).split())


def inline_generated_tables(text: str) -> str:
    pattern = re.compile(r"\\input\{generated_lowshot/([^}]+)\}")

    def replacer(match: re.Match[str]) -> str:
        filename = match.group(1)
        candidate = GENERATED_DIR / filename
        if not candidate.suffix:
            candidate = candidate.with_suffix(".tex")
        return read_text(candidate)

    return pattern.sub(replacer, text)


def transform_section(text: str) -> str:
    text = inline_generated_tables(text)
    text = text.replace("{figures/", "{../../figures/")
    text = re.sub(r"\\begin\{table\}\[[^\]]+\]", r"\\begin{table}", text)
    text = re.sub(r"\\begin\{figure\}\[[^\]]+\]", r"\\begin{figure}", text)
    return text.strip()


def section_text(filename: str) -> str:
    return transform_section(read_text(SECTIONS_DIR / filename))


def build_document() -> str:
    abstract_body = extract_environment(
        read_text(SECTIONS_DIR / "abstract.tex"), "abstract"
    )
    introduction = section_text("introduction.tex")
    related_work = section_text("related_work.tex")
    method = section_text("method.tex")
    experiments = section_text("experiments.tex")
    conclusion = section_text("conclusion.tex")
    appendix = section_text("appendix.tex")

    return f"""\\documentclass[a4paper,fleqn]{{cas-sc}}

\\usepackage[authoryear]{{natbib}}
\\usepackage{{graphicx}}
\\usepackage{{float}}
\\usepackage{{color}}
\\usepackage{{setspace}}
\\usepackage{{booktabs}}
\\usepackage{{array}}
\\usepackage{{multirow}}
\\usepackage{{amsmath,amssymb,amsfonts}}
\\usepackage{{enumitem}}
\\usepackage{{xcolor}}
\\usepackage{{url}}

\\begin{{document}}
\\let\\WriteBookmarks\\relax
\\def\\floatpagepagefraction{{1}}
\\def\\textpagefraction{{.001}}
\\shorttitle{{Reproducible DINOv2 Adaptation for Scarce-Label RSSC}}
\\shortauthors{{Hou}}

\\title[mode = title]{{Reproducible Selective Adaptation of DINOv2 for Scarce-Label Remote Sensing Scene Classification}}

\\author[1]{{Chao Hou}}
\\credit{{Conceptualization, methodology, software, validation, visualization, writing - original draft.}}

\\address[1]{{School of Cybersecurity, Xi'an Polytechnic University, Xi'an, Shaanxi, China}}

\\begin{{abstract}}
{abstract_body}
\\end{{abstract}}

\\begin{{coverletter}}
Dear Editors,
\\newline

Please consider our manuscript ``Reproducible Selective Adaptation of DINOv2 for Scarce-Label Remote Sensing Scene Classification'' for publication in Computers \\& Geosciences.
\\newline

This manuscript addresses a practical geocomputing problem: scarce-label remote sensing scene classification under public-data, fixed-protocol evaluation. Rather than proposing another scene-classification architecture, we contribute a reproducible computational workflow that couples DINOv2-Base selective adaptation with persistent split manifests, scriptable multi-seed aggregation, and manuscript-rebuild assets.
\\newline

We believe the work fits Computers \\& Geosciences for three reasons. First, it addresses geospatial image analysis on public remote sensing benchmarks. Second, its central contribution is a reusable computational workflow rather than architecture-only benchmarking. Third, the code, configuration, and reproduction assets are publicly available at \\url{{{PUBLIC_REPO_URL}}} under the MIT License, with a reviewer-safe archive retained for inspection convenience.
\\newline

Under one fixed class-balanced protocol, we observe a strong overall-accuracy increase on AID from 0.9179 to 0.9413 and a modest positive increase on NWPU-RESISC45 from 0.8721 to 0.8790, presented as reproducible workflow outcomes rather than universal performance claims. Same-backbone ablations show that selective finetuning provides the primary gain, while the adapter mainly improves stability and the feature-center regularizer improves consistency.
\\newline

This manuscript has not been published previously and is not under consideration elsewhere.
\\newline

The author has approved the manuscript and agrees with its submission to Computers \\& Geosciences.
\\newline

Sincerely,
\\newline

Chao Hou
\\newline

School of Cybersecurity, Xi'an Polytechnic University
\\newline

2446099877@qq.com
\\end{{coverletter}}

\\begin{{highlights}}
\\item Fixed public split manifests and scripted multi-seed aggregation support reproducible low-shot remote sensing evaluation.
\\item The workflow delivers strong gains on AID and modest gains on NWPU under identical seed-controlled splits.
\\item Partial finetuning is the main gain source under the evaluated scarce-label protocol.
\\item The workflow package includes rebuildable tables, figures, and reviewer-ready reproduction assets.
\\item Final training remains feasible on a single 8 GB GPU with only about 7.5M trainable parameters.
\\end{{highlights}}

\\begin{{keywords}}
remote sensing scene classification \\sep scarce-label learning \\sep reproducibility \\sep DINOv2 \\sep transfer learning \\sep geocomputation
\\end{{keywords}}

\\maketitle

\\printcredits

\\doublespacing

{introduction}

{related_work}

{method}

{experiments}

{conclusion}

\\section{{Acknowledgments}}
This work currently has no external funding to declare.

\\newpage

\\section*{{Code availability}}
Name of the code/library: Treatise scarce-label remote sensing classification workflow.

Contact: Chao Hou (2446099877@qq.com).

Hardware requirements: all final DINOv2 experiments were trained on a single NVIDIA RTX 4060 Ti 8 GB GPU with gradient checkpointing and gradient accumulation.

Program language: Python 3.11.

Software required: PyTorch environment defined by the project requirements file.

Program size: the release package contains the source modules, experiment scripts, configuration files, and manuscript-build assets required to reproduce the reported workflow, excluding raw datasets and trained checkpoints.

The source code, experiment configurations, split-generation logic, aggregation scripts, and manuscript-table rebuild scripts are publicly available at \\url{{{PUBLIC_REPO_URL}}}. A reviewer-safe archive containing the source modules, manifests, configurations, and manuscript-build assets is also retained for inspection convenience. The public repository is released under the MIT License.

{appendix}

\\bibliographystyle{{cas-model2-names}}
\\bibliography{{../../references}}

\\end{{document}}
"""


def main() -> None:
    args = parse_args()
    output_path = Path(args.output).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(build_document(), encoding="utf-8")
    print(f"wrote C&G submission manuscript to {output_path}")


if __name__ == "__main__":
    main()
