# C&G Editorial Manager Runbook

更新时间：`2026-03-23`

## 结论

- 当前 `paper_q2_cageo` 已具备一套可直接上传到 `Computers & Geosciences` 的投稿资产。
- 最稳妥的上传入口是：
  - [submission_ready/cageo](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo)
- `highlights.txt` 已从维护中的 highlights 草稿自动生成，可直接作为单独 `Highlights` 文件上传。

## 官方硬性项

依据 `Computers & Geosciences` 当前 `Guide for Authors` 与 CAS 模板要求，当前稿件至少应满足：

- `single-column` manuscript
- `double-spaced` submission PDF
- `author-date` bibliography
- `Highlights` 单独文件，`3` 到 `5` 条，每条 `<= 85` characters
- `Cover letter`
- `Authorship statement`
- `Generative AI` submission declaration
- 正文内 `Code availability` 段落
- 可公开访问的代码仓库链接与开源许可说明
- `Research/Application` 原始投稿正文建议控制在 `5,500` 词以内，最多上浮约 `10%`

## 当前本地对应文件

- 主稿 PDF：
  - [manuscript.pdf](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo/manuscript.pdf)
- 主稿 LaTeX 源：
  - [manuscript.tex](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo/manuscript.tex)
- 参考文献：
  - [references.bib](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo/references.bib)
- 图像资源目录：
  - [figures](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo/figures)
- 单独 highlights 文件：
  - [highlights.txt](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo/highlights.txt)
- Cover letter 草稿：
  - [cageo_cover_letter_draft.md](/D:/codex/treatise/paper_q2_cageo/docs/submission_packets/cageo_cover_letter_draft.md)
- Authorship statement：
  - [cageo_authorship_statement.md](/D:/codex/treatise/paper_q2_cageo/docs/submission_packets/cageo_authorship_statement.md)
- Generative AI 声明草稿：
  - [cageo_generative_ai_declaration_draft_2026-03-23.md](/D:/codex/treatise/paper_q2_cageo/docs/submission_packets/cageo_generative_ai_declaration_draft_2026-03-23.md)
- 官方要求与 scope 对齐说明：
  - [cageo_official_notes_2026-03-22.md](/D:/codex/treatise/paper_q2_cageo/docs/submission_packets/cageo_official_notes_2026-03-22.md)
  - [cageo_official_scope_check_2026-03-23.md](/D:/codex/treatise/paper_q2_cageo/docs/submission_packets/cageo_official_scope_check_2026-03-23.md)
- reviewer-safe 代码包：
  - [cageo_reviewer_code_packet.zip](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo_reviewer_code_packet.zip)
- 完整性清单：
  - [packet_manifest_sha256.txt](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo/packet_manifest_sha256.txt)
- 公开仓库：
  - [paper_q2_cageo](https://github.com/2446099877/paper_q2_cageo)

## Editorial Manager 上传映射

- `Article File`：
  - 上传 [manuscript.pdf](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo/manuscript.pdf)
- `Source Files`：
  - 上传 [manuscript.tex](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo/manuscript.tex)、[references.bib](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo/references.bib)、[figures](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo/figures) 以及 `cas-sc.cls`、`cas-common.sty`、`cas-model2-names.bst`
- `Highlights`：
  - 上传 [highlights.txt](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo/highlights.txt)
- `Cover Letter`：
  - 使用 [cageo_cover_letter_draft.md](/D:/codex/treatise/paper_q2_cageo/docs/submission_packets/cageo_cover_letter_draft.md) 内容
- `Authorship Statement`：
  - 使用 [cageo_authorship_statement.md](/D:/codex/treatise/paper_q2_cageo/docs/submission_packets/cageo_authorship_statement.md)
- `Generative AI Declaration`：
  - 使用 [cageo_generative_ai_declaration_draft_2026-03-23.md](/D:/codex/treatise/paper_q2_cageo/docs/submission_packets/cageo_generative_ai_declaration_draft_2026-03-23.md) 内容填系统声明
- `Supplementary Material for Review`：
  - 建议附上 [cageo_reviewer_code_packet.zip](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo_reviewer_code_packet.zip)

## 建议上传策略

- 必传：
  - `manuscript.pdf`
  - LaTeX source files
  - `highlights.txt`
  - `cover letter`
  - `authorship statement`
- 建议传：
  - `cageo_reviewer_code_packet.zip`
- 内部留档即可：
  - `packet_manifest_sha256.txt`
  - `packet_notes/` 下的状态、冻结、scope-check 文档

## 上传前最后检查

- 运行：
  - `D:\python311\python.exe D:\codex\treatise\paper_q2_cageo\scripts\validate_cageo_submission.py`
- 当前主稿粗略英文词数约 `4866`，仍在 `Research/Application` 原始投稿字数限制安全区间内
- 核对 GitHub 仓库首页是否公开、README 是否正常渲染、`LICENSE` 是否可见
- 核对当前作者信息、单位、邮箱、funding 是否仍与主稿一致
- 如需重新打包 reviewer 代码包，再执行：
  - `D:\python311\python.exe D:\codex\treatise\paper_q2_cageo\scripts\prepare_cageo_reviewer_code_packet.py`
