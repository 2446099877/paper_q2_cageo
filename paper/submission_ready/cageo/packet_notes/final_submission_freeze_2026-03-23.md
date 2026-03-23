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
- 当前作者口径：`Chao Hou`（单作者）
- 当前 funding 口径：`no external funding`

## Verification Snapshot

- 已验证的关键里程碑提交：
  - `0f5cc4a` (`finalize-cageo-validation-and-status-sync`)
  - `3e885bd` (`add-final-submission-freeze-snapshot`)
  - `11e42a9` (`fix-packet-freeze-copy-and-link-stability`)
  - `956069a` (`refine-code-availability-wording-and-rebuild-packet`)
- 单元测试：`python -m unittest discover -s tests`（`14` 项通过）
- 提交包占位符扫描：`outstanding_placeholders: none`
- PDF 产物：
  - [manuscript.pdf](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo/manuscript.pdf)

## Cross-File Consistency (Checked)

- 稿件 `Code availability` 已指向真实公开仓库并声明 `MIT`。
- cover letter 已同步公开仓库、许可证、reviewer-safe 口径。
- status 与 checklist 已同步：
  - 作者/基金条目已明确为“当前已确认，若后续变化再改”。
  - reviewer-safe 路径已固定为 zip 补充材料方案。

## Residual Human Confirmation (Final Pass)

- 如果作者、单位或联系信息后续变化，提交前再同步作者块。
- 如果 funding 状态后续变化，提交前再同步 Acknowledgments。
- Editorial Manager 上传时确认是否同时附上 reviewer-safe zip（建议附上）。

## Rollback Hint

- 若需回退到本轮冻结前，优先按上述里程碑提交选择回退点并重新生成投稿包，不要跨论文目录拷贝文件。
