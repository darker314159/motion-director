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
| lemo-opuscar | <https://github.com/lemomo-ai/lemo-opuscar> | — | MIT |
| opus-video-skills | <https://github.com/tuzhechen2005/opus-video-skills> | — | MIT |

`assets/catalog.json` 是一份**有日期的元数据快照**（`fetched_at: 2026-10-01T04:12:10Z`，
共 859 条记录，四个来源全部 `status: ok`），指向上述公开案例库的视频标题、作者、
播放链接与提示词原文地址。该快照**不含任何视频文件本体**，仅存元数据与链接。
每个来源都带 `sha256` 校验值，可与上游原始数据比对。

## 本仓库的改动

- 新增 `LICENSE`（MIT，以 `darker314159` 名义）
- 新增 `README.md` 与本文件
- 未修改 skill 逻辑代码；原始 16 个文件保持原样

## 免责声明

- 视频案例的著作权归各原作者所有，本仓库仅索引元数据与来源链接。
- 使用者需自行确认所选参考素材的授权范围。
- 本 skill 不安装任何依赖，不自动下载外部素材。
