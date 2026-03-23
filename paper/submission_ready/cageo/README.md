# Computers & Geosciences Submission Packet

This directory organizes the current `Computers & Geosciences` submission materials into one place.

## Main Files

- `manuscript.tex`: single-file Elsevier CAS-style manuscript
- `highlights.txt`: ready-to-upload highlights file
- `references.bib`: bibliography used by the manuscript
- `figures/`: figure assets referenced by the manuscript
- `cas-sc.cls`, `cas-common.sty`, `cas-model2-names.bst`: template support files
- `packet_notes/`: official notes, review quickstart, scope-check note, and support drafts
- `packet_manifest_sha256.txt`: integrity manifest for the packet files

## Notes

- This packet was generated automatically from the current project sources.
- The current packet already passes the local placeholder scan.
- Before final submission, verify that the current single-author metadata is still correct and that the repository landing page remains publicly accessible.
- Raw datasets are not redistributed in this packet; reviewers should obtain AID and NWPU-RESISC45 from their original public sources and then use the included manifests and scripts for reproduction.
- `highlights.txt` is synchronized from the maintained highlights draft and is ready for Editorial Manager upload.
- `packet_manifest_sha256.txt` can be retained internally to verify the integrity of archived packet files after zipping or transfer.
- One-click rebuild + compile script:
  `D:\python311\python.exe D:\codex\treatise\paper_q2_cageo\scripts\compile_cageo_pdf.py`
- Placeholder readiness check:
  `D:\python311\python.exe D:\codex\treatise\paper_q2_cageo\scripts\check_cageo_packet_readiness.py`
- Full sequential validation:
  `D:\python311\python.exe D:\codex\treatise\paper_q2_cageo\scripts\validate_cageo_submission.py`
