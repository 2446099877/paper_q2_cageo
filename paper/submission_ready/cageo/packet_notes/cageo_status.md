# C&G Submission Status

更新时间：`2026-03-23`

## Completed

- 新论文默认目标已切到 `Computers & Geosciences`
- 新论文已迁入独立工作区：
  - [paper_q2_cageo](/D:/codex/treatise/paper_q2_cageo)
- 官方模板已下载到：
  - [CAGEO_LaTeXTemplate-main](/D:/codex/treatise/paper_q2_cageo/paper/cageo_template/CAGEO_LaTeXTemplate-main)
- 新的 `C&G` 口径章节已落地：
  - [sections](/D:/codex/treatise/paper_q2_cageo/paper/sections)
- 单文件 `C&G` 稿已生成：
  - [treatise_cageo_submission.tex](/D:/codex/treatise/paper_q2_cageo/paper/cageo_template/CAGEO_LaTeXTemplate-main/treatise_cageo_submission.tex)
- `C&G` 提交包已生成：
  - [submission_ready/cageo](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo)
- 本机已成功编译出 `C&G` PDF：
  - [manuscript.pdf](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo/manuscript.pdf)
- 一键重建脚本已补齐：
  - [compile_cageo_pdf.py](/D:/codex/treatise/paper_q2_cageo/scripts/compile_cageo_pdf.py)
- 占位符检查脚本已补齐：
  - [check_cageo_packet_readiness.py](/D:/codex/treatise/paper_q2_cageo/scripts/check_cageo_packet_readiness.py)
- 当前 `C&G` 提交包已通过本地占位符扫描：
  - `outstanding_placeholders: none`
- 当前提交版 PDF 已按官方要求启用双倍行距与 line numbering
- 第二篇独立 reviewer-safe 代码包已生成：
  - [cageo_reviewer_code_packet](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo_reviewer_code_packet)
  - [cageo_reviewer_code_packet.zip](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo_reviewer_code_packet.zip)
- 第二篇默认开源许可已准备：
  - [LICENSE](/D:/codex/treatise/paper_q2_cageo/LICENSE)
- 第二篇公开代码仓库已上线：
  - `https://github.com/2446099877/paper_q2_cageo`
- 第二篇轻量自检已补齐并通过：
  - `python -m unittest discover -s tests`
- 第二篇本地 guardrail 测试已扩展到：
  - reviewer-safe code release wording
  - stale template wording cleanup
  - real GitHub repository URL injection
  - highlights consistency and length
  - manuscript submission metadata sections
  - word-count guardrail
  - Editorial Manager bundle completeness
  - 当前 `19` 个测试全部通过
- 已完成一轮最终 LaTeX warning 复查：
  - 现存 warning 主要来自 `cas-sc` 模板排版与长段落换行
  - 属于非阻塞噪声，不影响 PDF 产出与提交内容完整性
- 独立工作区内已完成一条新实验扩展：
  - `AID low20 + DINOv2-small + adapter_ft2` 三 seed `0.9262 ± 0.0020`
- 摘要、引言、结论已完成一轮 `geocomputing / reproducibility` 口径强化
- `related_work`、`experiments`、cover letter、highlights 已完成第二轮 `C&G` 编辑口径收束
- `NWPU` 小增益的表述已收敛为更保守的跨数据集结论
- reviewer quickstart、results snapshot、appendix 已完成第三轮一致性收口
- `Highlights` 已压缩到官方 `<= 85` characters 限制，并生成单独上传文件：
  - [highlights.txt](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo/highlights.txt)
- `Editorial Manager` 上传 runbook 已补齐：
  - [cageo_editorial_manager_runbook_2026-03-23.md](/D:/codex/treatise/paper_q2_cageo/docs/submission_packets/cageo_editorial_manager_runbook_2026-03-23.md)
- `Generative AI` 投稿声明草稿已补齐：
  - [cageo_generative_ai_declaration_draft_2026-03-23.md](/D:/codex/treatise/paper_q2_cageo/docs/submission_packets/cageo_generative_ai_declaration_draft_2026-03-23.md)
- `Competing interest` 与 `Data availability` 声明草稿已补齐
- 当前主稿已补齐：
  - corresponding author email
  - funding statement
  - code availability
  - data availability
  - competing interest
  - generative AI declaration
- 当前 guardrail 统计：
  - abstract `238` words
  - main body `2881` words
  - keywords `6`
- `Editorial Manager` 上传 bundle 已生成：
  - [cageo_editorial_manager_bundle](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo_editorial_manager_bundle)
  - [cageo_editorial_manager_bundle.zip](/D:/codex/treatise/paper_q2_cageo/paper/submission_ready/cageo_editorial_manager_bundle.zip)
- 已创建投稿前冻结快照：
  - [final_submission_freeze_2026-03-23.md](final_submission_freeze_2026-03-23.md)
- 已按官方最新期刊口径完成一轮 scope 对齐核对：
  - [cageo_official_scope_check_2026-03-23.md](cageo_official_scope_check_2026-03-23.md)

## Current Positioning

- 当前稿件定位不是“视觉通用模型轻量化”
- 当前稿件定位也不是“新的遥感专用结构创新”
- 当前定位是：
  - `scarce-label geospatial image analysis`
  - `reproducible workflow`
  - `public data + fixed manifests + multi-seed aggregation`
  - `commodity-GPU feasible adaptive transfer`
  - `rebuildable geocomputing evidence generation`
  - `reviewer-safe software-style reproduction assets`
  - `workspace-local outputs without polluting the first paper`

## Pending But Ready To Fill

- 如果作者、单位、联系方式后续发生变化，需要在投稿前同步作者块
- 如果 funding 状态后续变化，需要同步更新 `Funding` 段落与上传声明
- 如果正式上线仓库时不想使用 `MIT`，需要在公开前统一替换许可文本

## Residual Risks

- 当前 `NWPU` 增益仍偏小，摘要和结论必须继续保持克制
- `DINOv2-small` 的 `NWPU` 三 seed 已补齐，但结果相对 `ConvNeXt-Tiny` 为 `-0.0071 OA`，因此这条线更适合作为补充负结果，而不是正文主卖点
- `C&G` 模板目前能成功出 PDF，但仍有少量非阻塞版式 warning
- 当前 warning 已复核为模板级非阻塞噪声；仅在极致版面优化时再处理
- 当前作者与联系信息已在主稿与 bundle 中落地；如果作者列表后续变化，仍需在正式投稿前统一重写
- reviewer-safe 方案已定为 zip 补充材料；正式投稿时需确认是否一起上传
- 依据 `Computers & Geosciences` 官方 Guide for Authors，正文需要包含可下载代码的仓库链接并标明开源许可；当前本地源码已具备此条件，但正式投稿前仍应复查仓库首页与 README 展示效果
- 当前仍有非阻塞 `lineno`/首屏排版 warning；属于 CAS 模板噪声，不影响投稿，但若追求极致版式可继续微调

## Current Default Commands

- 重建并编译 `C&G` PDF：
  - `D:\python311\python.exe D:\codex\treatise\paper_q2_cageo\scripts\compile_cageo_pdf.py`
- 仅检查 `C&G` 提交包占位符：
  - `D:\python311\python.exe D:\codex\treatise\paper_q2_cageo\scripts\check_cageo_packet_readiness.py`
- 串行验证 `C&G` 提交包：
  - `D:\python311\python.exe D:\codex\treatise\paper_q2_cageo\scripts\validate_cageo_submission.py`
- 单独重建 Editorial Manager 上传 bundle：
  - `D:\python311\python.exe D:\codex\treatise\paper_q2_cageo\scripts\prepare_cageo_editorial_manager_bundle.py`
