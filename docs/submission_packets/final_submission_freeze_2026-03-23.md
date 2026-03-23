# Final Submission Freeze (2026-03-23)

更新时间：`2026-03-23`

## Freeze Scope

- 工作区：`D:\codex\treatise\paper_q2_cageo`
- 目标期刊：`Computers & Geosciences`
- 本记录用于“投稿前冻结快照”，确保口径、链接、许可证、复现入口一致。

## Frozen Facts

- 公开仓库：`https://github.com/2446099877/paper_q2_cageo`
- 开源许可：`MIT`
- reviewer-safe 方案：`paper/submission_ready/cageo_reviewer_code_packet.zip`
- Editorial Manager bundle：`paper/submission_ready/cageo_editorial_manager_bundle`
- 当前作者口径：`Chao Hou`（单作者）
- 当前 funding 口径：`no specific grant`

## Verification Snapshot

- 已验证的代表性里程碑提交（非穷尽）：
  - `efe65d8` (`harden-cageo-submission-compliance-pack`)
  - `f74ee9b` (`enable-line-numbered-cageo-submission-mode`)
  - `08b8a2b` (`make-cageo-packet-self-auditable`)
  - `c9cf35d` (`add-official-cageo-scope-alignment-note`)
- 单元测试：`python -m unittest discover -s tests`（`19` 项通过）
- 提交包占位符扫描：`outstanding_placeholders: none`
- 字数 guardrail：
  - abstract `238` words
  - main body `2881` words
  - keywords `6`
- PDF 产物：
  - [manuscript.pdf](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo/manuscript.pdf)
- 上传 bundle：
  - [cageo_editorial_manager_bundle](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo_editorial_manager_bundle)
  - [cageo_editorial_manager_bundle.zip](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo_editorial_manager_bundle.zip)

## Cross-File Consistency (Checked)

- 稿件 `Code availability` 已指向真实公开仓库并声明 `MIT`。
- 稿件已补齐 `Funding`、`Data availability`、`Declaration of competing interest`、`Declaration of generative AI...` 段落。
- cover letter 已同步公开仓库、许可证、reviewer-safe 口径。
- status 与 checklist 已同步：
  - 作者/基金条目已明确为“当前已确认，若后续变化再改”。
  - reviewer-safe 路径已固定为 zip 补充材料方案。
  - Editorial Manager bundle 已纳入验证链并自动生成。

## Residual Human Confirmation (Final Pass)

- 如果作者、单位或联系信息后续变化，提交前再同步作者块。
- 如果 funding 状态后续变化，提交前再同步 `Funding` 段落与上传声明。
- Editorial Manager 上传时确认是否同时附上 reviewer-safe zip（建议附上）。

## Rollback Hint

- 若需回退到本轮冻结前，优先按上述里程碑提交选择回退点并重新生成投稿包，不要跨论文目录拷贝文件。
