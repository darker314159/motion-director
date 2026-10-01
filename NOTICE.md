# 出处与致谢 / Attribution

本仓库收录的 `motion-director` skill 最初由第三方团队 **LemoLab** 创作与发布，
黑蜂情感 AI（`darker314159`）在取得作者授权后重新整理发布。

## 原始作者

- **LemoLab**（LemoLab / lemomo-ai）
- 上游项目：<https://github.com/lemomo-ai/lemo-opuscar>
- 原始分发包未附带独立 LICENSE 文件

## 第三方素材库

本 skill 的参考检索功能依赖以下公开视频案例库（均为 MIT 许可，
完整许可文本见 [`references/upstream-licenses.md`](references/upstream-licenses.md)）：

| 素材库 | 地址 | 记录数 | 许可 |
|---|---|---|---|
| awesome-opus5-5-videos | <https://github.com/yihui-dev/awesome-opus5-5-videos> | 475 | MIT |
| awesome-ai-motion | <https://github.com/guanmo-ai/awesome-ai-motion> | 384 | MIT |
| lemo-opuscar | <https://github.com/lemomo-ai/lemo-opuscar> | 43 | MIT |
| opus-video-skills | <https://github.com/tuzhechen2005/opus-video-skills> | — | MIT |

### 在线案例库（非 JSON 源）

| 案例库 | 地址 | 性质 |
|---|---|---|
| Skillry Opus 5.5 | <https://skillry.dev/ai-videos/opus-5-5> | 实时网页检索，不参与 `catalog.py refresh` |

Skillry 是**在线页面**而非代码仓库，本仓库不镜像其内容，仅在 skill 运行时按需读取页面并
保存必要元数据与链接。页面上的 Original 与 Remake 是不同版本，使用时会分别标注。
yihui 的 475 条记录中带有 `skillry_url` 字段，属**间接收录**，不代表 Skillry 页面已刷新或
视频已被观看——该边界由 `catalog.json` 的 `gallery_sources` 字段显式标注。

`assets/catalog.json` 是一份**有日期的元数据快照**（`fetched_at: 2026-10-01T04:12:10Z`），
三个 JSON 来源全部 `status: ok`：yihui 475 + guanmo 384 + lemo 43 = 902 条原始记录，
按 X 原帖 ID 跨库去重后为 **837 个条目**（794 video + 43 style），指向上述公开案例库的
视频标题、作者、播放链接与提示词原文地址。该快照**不含任何视频文件本体**，仅存元数据与链接。
每个 JSON 来源都带 `sha256` 校验值，可与上游原始数据比对。

## 本仓库的改动

- 新增 `LICENSE`（MIT，以 `darker314159` 名义）
- 新增 `README.md` 与本文件
- 未修改 skill 逻辑代码；原始 16 个文件保持原样

## 版本记录

| 版本 | 日期 | 变更 |
|---|---|---|
| v1.0 | 2026-10-01 | 首次收录（16 文件，catalog 962KB） |
| v1.1 | 2026-10-01 | 上游更新：`SKILL.md` / `catalog.py` / `reference-selection.md` / `sources.md` / `catalog.json` 五文件替换。新增 **Skillry Opus 5.5 在线案例库**接入（475 条 yihui 记录附带 `skillry_url` + `gallery_sources` 边界声明），`catalog.json` 962KB → 1.03MB |
| v1.2 | 2026-10-01 | 上游更新：6 文件替换。**新增「一键成片」模式（`one_click`）**——全流程委托、自主决策、直接交付真实 MP4，三重确认改为内部审查但保留 `delegated` 记录；配套改动 `agents/openai.yaml`（描述与默认 prompt）、`assets/project-template.json`（新增 `mode` / `decision_log` 字段）、`sources.md` / `directing-and-qa.md` / `reference-selection.md` 的模式分支说明。`SKILL.md` 11KB → 15KB |

## 免责声明

- 视频案例的著作权归各原作者所有，本仓库仅索引元数据与来源链接。
- 使用者需自行确认所选参考素材的授权范围。
- 本 skill 不安装任何依赖，不自动下载外部素材。
