from __future__ import annotations

import re
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
            "cageo_editorial_manager_runbook_2026-03-23.md",
            "cageo_fill_once_form.md",
            "cageo_generative_ai_declaration_draft_2026-03-23.md",
            "cageo_highlights_draft.md",
            "cageo_official_notes_2026-03-22.md",
            "cageo_official_scope_check_2026-03-23.md",
            "cageo_pre_submission_checklist.md",
            "cageo_status.md",
        ]
        missing = [name for name in required if not (notes_dir / name).exists()]
        self.assertEqual(missing, [], msg=f"Missing packet notes: {missing}")

    def test_submission_packet_contains_support_docs(self) -> None:
        notes_dir = ROOT / "paper" / "submission_ready" / "cageo" / "packet_notes"
        required = [
            "cageo_editorial_manager_runbook_2026-03-23.md",
            "cageo_fill_once_form.md",
            "cageo_generative_ai_declaration_draft_2026-03-23.md",
            "cageo_official_scope_check_2026-03-23.md",
            "reviewer_reproduction_quickstart.md",
            "results_snapshot.md",
            "final_submission_freeze_2026-03-23.md",
        ]
        missing = [name for name in required if not (notes_dir / name).exists()]
        self.assertEqual(missing, [], msg=f"Missing packet support docs: {missing}")

    def test_submission_packet_manifest_exists(self) -> None:
        manifest = ROOT / "paper" / "submission_ready" / "cageo" / "packet_manifest_sha256.txt"
        self.assertTrue(manifest.exists())
        text = manifest.read_text(encoding="utf-8")
        self.assertIn("highlights.txt", text)
        self.assertIn("manuscript.tex", text)
        self.assertIn("packet_notes/cageo_status.md", text)

    def test_submission_pdf_exists(self) -> None:
        self.assertTrue((ROOT / "paper" / "submission_ready" / "cageo" / "manuscript.pdf").exists())

    def test_highlights_are_submission_ready(self) -> None:
        draft_path = ROOT / "docs" / "submission_packets" / "cageo_highlights_draft.md"
        draft_highlights = [
            " ".join(line.strip()[2:].split())
            for line in draft_path.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith("- ")
        ]
        self.assertGreaterEqual(len(draft_highlights), 3)
        self.assertLessEqual(len(draft_highlights), 5)
        for item in draft_highlights:
            self.assertLessEqual(
                len(item),
                85,
                msg=f"Highlight exceeds 85 characters: {item}",
            )

        manuscript_path = ROOT / "paper" / "submission_ready" / "cageo" / "manuscript.tex"
        manuscript = manuscript_path.read_text(encoding="utf-8")
        match = re.search(
            r"\\begin\{highlights\}(.*?)\\end\{highlights\}",
            manuscript,
            flags=re.S,
        )
        self.assertIsNotNone(match, msg="Generated manuscript is missing highlights block")
        manuscript_highlights = [
            " ".join(item.split())
            for item in re.findall(r"\\item\s+([^\n]+)", match.group(1))
        ]
        self.assertEqual(manuscript_highlights, draft_highlights)

        upload_path = ROOT / "paper" / "submission_ready" / "cageo" / "highlights.txt"
        self.assertTrue(upload_path.exists())
        upload_highlights = [
            " ".join(line.strip()[2:].split())
            for line in upload_path.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith("- ")
        ]
        self.assertEqual(upload_highlights, draft_highlights)

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
