from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_REPO_URL = "https://github.com/2446099877/paper_q2_cageo"


class CageoReleaseTests(unittest.TestCase):
    def test_license_exists(self) -> None:
        self.assertTrue((ROOT / "LICENSE").exists())

    def test_release_metadata_files_exist(self) -> None:
        self.assertTrue((ROOT / ".gitignore").exists())
        self.assertTrue((ROOT / "CITATION.cff").exists())

    def test_reviewer_packet_script_exists(self) -> None:
        self.assertTrue((ROOT / "scripts" / "prepare_cageo_reviewer_code_packet.py").exists())

    def test_submission_packet_notes_exist(self) -> None:
        notes_dir = ROOT / "docs" / "submission_packets"
        required = [
            "cageo_authorship_statement.md",
            "cageo_cover_letter_draft.md",
            "cageo_highlights_draft.md",
            "cageo_official_notes_2026-03-22.md",
            "cageo_pre_submission_checklist.md",
            "cageo_status.md",
        ]
        missing = [name for name in required if not (notes_dir / name).exists()]
        self.assertEqual(missing, [], msg=f"Missing packet notes: {missing}")

    def test_submission_pdf_exists(self) -> None:
        self.assertTrue((ROOT / "paper" / "submission_ready" / "cageo" / "manuscript.pdf").exists())

    def test_no_stale_springer_wording_remains(self) -> None:
        checked_files = [
            ROOT / "paper" / "sections" / "appendix.tex",
            ROOT / "docs" / "reviewer_reproduction_quickstart.md",
            ROOT / "docs" / "results_snapshot.md",
            ROOT / "scripts" / "build_cageo_submission.py",
        ]
        for path in checked_files:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(
                "Springer-style",
                text,
                msg=f"Stale template wording remains in {path}",
            )

    def test_generated_manuscript_mentions_code_release_plan(self) -> None:
        manuscript = (
            ROOT / "paper" / "submission_ready" / "cageo" / "manuscript.tex"
        ).read_text(encoding="utf-8")
        self.assertIn("MIT License", manuscript)
        self.assertIn("reviewer-safe archive", manuscript)
        self.assertIn(PUBLIC_REPO_URL, manuscript)
        self.assertNotIn("camera-ready materials", manuscript)
        self.assertNotIn("planned public release", manuscript)

    def test_readme_avoids_local_absolute_links(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("](/D:/", readme)

    def test_citation_uses_real_repository_url(self) -> None:
        citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
        self.assertIn(PUBLIC_REPO_URL, citation)
        self.assertNotIn("TO_BE_FILLED", citation)


if __name__ == "__main__":
    unittest.main()
