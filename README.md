# Motion Director

> 用**真实优秀视频**驱动的 Motion Graphics 制作导演 skill。
> 不凭空编画面——先让你从 859 条真实案例里挑参考，再设计分镜，最后出片验收。

一个把「需求 → 参考 → 方案 → 关键帧 → 成片」串成闭环的 Agent Skill。
核心约束一句话：**没看过参考就不能说看过，没确认过方案就不许写场景代码。**

---

## 🎬 它解决什么问题

做动态视频最常见的翻车方式：

- AI 自我感觉良好地编了一段动画，你事后才发现风格不对
- 文字溢出、主体太小、转场生硬，但没人提前说过
- 做到一半你改主意了，前面的确认全部作废，却没重开对应环节
- 声称"参考了这个爆款视频"，其实只看了封面

这个 skill 用 **9 阶段审批流**堵住上述每一个洞。

## 🔁 9 阶段流程

```
需求澄清 → 环境体检 → 真实参考候选 → 用户选参考
   → 导演方案 → 用户确认方案
   → 三张关键帧 + 动态样片 → 用户确认视觉
   → 全片制作 → 成片验收
```

**三个不可跳过的确认门**（`approvals` 字段记录状态、原话、适用范围、revision）：

| 门 | 触发条件 | 静默行为 |
|---|---|---|
| 参考确认 | 必须真正看过视频 | 只见封面 → 标「仅元数据初筛」 |
| 方案确认 | `motion-project.json` 完整 | 沉默 ≠ 确认 |
| 视觉确认 | 静帧 + 3–5s 样片 | 静帧不能证明运动质量 |

**失效规则**（改了什么就重开哪个门，不必从头再来）：

- 参考/风格变了 → 导演 + 视觉确认失效
- 时长/核心文案变了 → 受影响镜头失效
- 仅调音量 → 视觉确认**不**重开

## 🛠 技术选型

`scripts/doctor.py` 先体检再动工，四条渲染路线任选：

| 路线 | 入口 | 适用 |
|---|---|---|
| Remotion / HyperFrames | 原生渲染 | React 生态成片 |
| HTML / CSS / SVG | `scripts/render.mjs` | 纯网页动效 |
| Canvas / Three.js / WebGL | `scripts/render.mjs` | 3D、粒子、shader |
| Python Manim | 原生渲染 | 数学、图表、讲解 |

HTML 系路线需暴露 `window.READY` / `window.DUR` / `window.render(t)`，契约见
`assets/html-contract.html`。

**skill 不安装任何依赖**——只报告环境缺什么，由你决定装不装。

## 📦 快速安装

```bash
git clone https://github.com/darker314159/motion-director.git
cp -r motion-director ~/.agents/skills/          # Claude Code / Codex / Cursor 通用
```

Claude Code / WorkBuddy 会自动识别 `SKILL.md` 并按描述触发。

## 🗂 目录结构

```
motion-director/
├── SKILL.md                    # 工作流骨架（9 阶段 + 铁律）
├── agents/openai.yaml          # ChatGPT / Codex 接口声明
├── assets/
│   ├── catalog.json            # 859 条真实案例元数据快照（962KB）
│   ├── html-contract.html      # 渲染契约示例
│   ├── icon.svg
│   └── project-template.json   # motion-project.json 模板
├── references/
│   ├── directing-and-qa.md     # 导演与验收规范
│   ├── reference-selection.md  # 参考检索与选择
│   ├── sources.md              # 来源映射
│   ├── stack-and-environment.md# 技术选型与环境
│   └── upstream-licenses.md    # 四个上游库完整 MIT 许可
└── scripts/
    ├── doctor.py               # 环境体检
    ├── catalog.py              # 刷新/检索案例库
    ├── check_plan.py           # 记录完整性校验
    ├── inspect_media.py        # 媒体信息探测
    └── render.mjs              # HTML 系渲染器
```

长文档全部拆到 `references/`，`SKILL.md` 只留骨架——不撑爆上下文。

## 🔄 刷新案例库

内置 `catalog.json` 是 **2026-10-01** 的快照。联网时可刷新到项目缓存：

```bash
python scripts/catalog.py refresh --out <project>/research/catalog.json

python scripts/catalog.py search \
  --catalog <project>/research/catalog.json \
  --query "聊天 产品 界面 动态排版" \
  --category product --duration 30 --limit 12 \
  --out <project>/research/candidates.json \
  --board <project>/research/candidates.html
```

刷新失败会**如实报告日期和失败源**，不会拿旧数据假装是新的。

## 📜 出处与授权

本 skill 最初由 **LemoLab** 创作，黑蜂情感 AI 在取得作者授权后重新整理发布。
内嵌案例库来自 4 个 MIT 许可的公开项目（859 条记录，含 sha256 校验）。

**`assets/catalog.json` 只存元数据和链接，不含任何视频文件本体。**
视频著作权归各原作者，选素材前请自行确认授权范围。

完整说明见 [NOTICE.md](NOTICE.md) 与 [references/upstream-licenses.md](references/upstream-licenses.md)。

## 📄 License

MIT © 2026 darker314159
