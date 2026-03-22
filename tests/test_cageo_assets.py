from __future__ import annotations

import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class CageoAssetTests(unittest.TestCase):
    def test_required_paper_figures_exist(self) -> None:
        figure_dir = ROOT / "paper" / "figures"
        required = [
            "aid_low20_baseline_confusion.png",
            "aid_low20_full_confusion.png",
            "nwpu_low20_baseline_confusion.png",
            "nwpu_low20_full_confusion.png",
            "aid_low20_baseline_activation.png",
            "aid_low20_full_activation.png",
            "nwpu_low20_baseline_activation.png",
            "nwpu_low20_full_activation.png",
        ]
        missing = [name for name in required if not (figure_dir / name).exists()]
        self.assertEqual(missing, [], msg=f"Missing C&G figures: {missing}")

    def test_generated_tables_exist(self) -> None:
        generated = ROOT / "paper" / "generated_lowshot"
        required = [
            "main_results.tex",
            "ablation_results.tex",
            "stability_results.tex",
            "seedwise_results.tex",
            "complexity_results.tex",
        ]
        missing = [name for name in required if not (generated / name).exists()]
        self.assertEqual(missing, [], msg=f"Missing generated tables: {missing}")

    def test_submission_manuscript_has_no_input_commands(self) -> None:
        manuscript = (
            ROOT / "paper" / "submission_ready" / "cageo" / "manuscript.tex"
        ).read_text(encoding="utf-8")
        self.assertNotIn("\\input{", manuscript)
        self.assertIn("\\bibliography{references}", manuscript)

    def test_abstract_avoids_citations(self) -> None:
        abstract_text = (ROOT / "paper" / "sections" / "abstract.tex").read_text(encoding="utf-8")
        self.assertNotIn("\\cite", abstract_text)

    def test_all_citation_keys_exist_in_bib(self) -> None:
        bib_text = (ROOT / "paper" / "references.bib").read_text(encoding="utf-8")
        tex_text = "\n".join(
            path.read_text(encoding="utf-8")
            for path in (ROOT / "paper" / "sections").glob("*.tex")
        )
        bib_keys = set(re.findall(r"@\w+\{([^,]+),", bib_text))
        cite_keys: set[str] = set()
        for group in re.findall(r"\\cite\{([^}]+)\}", tex_text):
            cite_keys.update(part.strip() for part in group.split(","))
        missing = sorted(cite_keys - bib_keys)
        self.assertEqual(missing, [], msg=f"Missing citation keys: {missing}")


if __name__ == "__main__":
    unittest.main()
