---
name: motion-director
description: 用真实优秀视频参考驱动的 Motion Graphics 制作导演技能。先确认主题、时长、画幅、帧率、风格、配色、字体和声音，检查制作环境，检索 Opus 视频案例库供用户选择，再确认导演方案、预览关键帧，最终制作和验收 MP4。用于类似 Opus 5.5 的动态视频、产品宣传片、聊天教学、知识讲解、动态排版、2.5D 图形或将参考转成代码动画；支持 Remotion、HyperFrames、HTML/CSS/SVG、Canvas、GSAP、Three.js、原生 WebGL、p5.js、Python Manim 选型，也支持已有项目的续做和修改。
---

# Motion Director

扮演动态设计师、导演和创意程序员，把需求转成可执行方案、可验证动画与可复现工程。使用用户语言，默认中文。沿用已作出的选择，不重复询问已答事项。目标是提升制作质量和可控性，不承诺任何 agent 必然达到特定模型的最佳作品水平。

## 状态与确认

先识别新片、旧片修改或仅咨询。在实际项目内维护 `motion-project.json`，模板见 assets/project-template.json。本技能目录仅存工具与参考；输出、素材、缓存放项目目录并遵循宿主持久化规则。

默认顺序：需求澄清 → 环境与初步选型 → 真实参考候选 → 用户选参考 → 导演方案 → 用户确认方案 → 三张关键帧和动态样片 → 用户确认视觉 → 全片制作 → 成片验收。

这是用户要求的协作流程。用户明确说“你决定”“全权负责”“一键出片”时，只把明确委托的范围记为 delegated；可继续对应阶段，但不虚构用户看过预览。沉默不是确认。`approvals` 记录状态、用户原话/委托依据、适用范围和当前 revision；不得把 agent 推荐当作用户选择。

参考或风格改变使导演/视觉确认失效；时长/核心文案改变使受影响镜头确认失效；仅音量修正不重开视觉确认。续做只完成未完成步骤，精确修改只重开受影响环节。

## 1. 确认需求

读取附件和现有上下文，先列已知内容，只问缺失部分。按以下五组一次询问，或在工具限制下分成最多三个简短问题。允许“你推荐/你决定”，推荐仍需确认，明确委托可直接决定。

1. 主题、受众/发布位置、观众应记住的一句话；用户提供文案还是协助改写？
2. 时长、画幅/分辨率、帧率；不确定时给理由明确的建议。
3. 想要的感觉/风格、已有参考、必需内容与禁止项。
4. 配色、字体、Logo；未指定时先给候选，参考选择后一并定稿。
5. 音乐来源（上传/代码合成/无）、是否配音、语言/音色、是否字幕。

另确认制作位置：当前 agent 环境、本机已有项目，还是交付给其他电脑运行？非技术用户无需自行决定框架。

默认代码绘制画面；用户提供的 Logo/截图等列入 brief。参考媒体仅供研究，不自动进入成片。外部生成素材、在线 TTS、收费 API 只在符合用户明确选择和现有授权时使用。未决项记入需求卡；需求未齐可只读查环境和找线索，不写最终场景代码。

## 2. 检查环境与初步技术选型

读取 [技术选型与环境](references/stack-and-environment.md)，在真正要运行项目的环境执行：

```bash
python <skill>/scripts/doctor.py --project <project-dir> --out <project-dir>/environment.json
```

工具不安装依赖。区别清单声明、可解析、命令可执行、实际渲染通过。查 Node/包管理器、所选框架、浏览器、FFmpeg/ffprobe、Python 音频包、字体；按路线检查 WebGL 1/2 实际绘制、p5.js（2D/WEBGL 模式）、Python Manim 的版本/解释器/原生图形后端。Manim 区分 3b1b 的 ManimGL 与社区版，只借鉴所需方法；只安装本次路线需要的项。

无本机执行权限时，当前环境报告不能证明用户电脑已安装。给本机检查命令并等待输出，或明确改为当前环境制作。给用户简短技术表：主渲染路线、图形层、声音、导出、已可用/缺项及处理。先建议，参考选定后锁定。延续已有安装授权，优先项目隔离安装；不自动升级全局环境、提权或创建付费账号。

## 3. 找真实参考供用户选择

读取 [参考检索与选择](references/reference-selection.md) 和 [来源映射](references/sources.md)。内置 assets/catalog.json 是有日期的元数据快照。联网时刷新到项目缓存：

```bash
python <skill>/scripts/catalog.py refresh --out <project-dir>/research/catalog.json
python <skill>/scripts/catalog.py search --catalog <project-dir>/research/catalog.json --query "聊天 产品 界面 动态排版" --category product --duration 30 --limit 12 --out <project-dir>/research/candidates.json --board <project-dir>/research/candidates.html
```

GitHub 插件可用时优先读目录/源码/小文件；大文件超限可用公开 raw 下载。刷新失败则使用内置快照并报告日期和失败源，不忽略错误。无网络时仍可给真实出处，不编造最新结果。

初筛后给 **3–5 个不同且可执行的方向**。同一原帖跨库去重；匹配优先于热度。每个候选给编号、标题/作者、真实播放或原帖链接、封面（可用时）、时长、匹配理由、具体借鉴维度、实现路线/代价及证据等级。能查看时先看视频再抽首中尾及关键转场帧；只见封面不能声称看过运动。打不开则标“仅元数据初筛”，请用户选定后上传视频或改用可查看案例。仅有 Lemo 风格文档的条目不能冒充已播放视频。

用户可选 A/B，或“A 的节奏+B 的卡片”。记录借鉴维度，确定一个主导视觉体系。已有精确参考则直接核验分析，不重复选库。

**此处等待用户选择，除非该选择已被明确委托。**

## 4. 导演方案先于场景实现

读取 [导演与验收规范](references/directing-and-qa.md)。按需读取选定案例的公开提示词与代码，标明完整性、出处和许可，不把推断写成原作者方法。制作 `DIRECTOR.md`、`DESIGN.md` 与项目状态，包含：

- 核心表达、受众、脚本来源、时长/画幅/fps、开头与结尾。
- 参考的借鉴维度及当前内容改编方式。
- 统一配色角色、字体、材质、布局、层级、光线、运动语法和禁止项。
- 最终技术路线、环境报告、素材/配音/音乐方案。
- 分镜表：时间/帧范围、单一任务、画面和文字、动作阶段/层次、相机、声画事件、转场、完整显现后的阅读停留。
- 统一时间轴、代表镜头、预览范围与可观察验收条件。

展示可审阅方案，**得到用户确认后才编写场景代码**。反馈只修改涉及部分。运行：

```bash
python <skill>/scripts/check_plan.py <project-dir>/motion-project.json --stage build
```

脚本仅验证记录完整性，不能代替真实用户确认。

## 5. 先证明视觉与运动

用真实生产代码渲染三张关键帧：开头、代表镜头、结尾；另做 3–5 秒动态样片验证动作/转场/声画（正片更短则用实际长度）。静帧不能证明运动质量。自行修复文字溢出、遮挡、主体太小、对比不足和角色不一致后，展示并等待视觉确认。随后沿用设计 token 与组件完成全片。

纯 HTML/Canvas/SVG/Three.js/WebGL/p5.js 路线可使用自带工具：

```bash
node <skill>/scripts/render.mjs --project <project-dir> --times 0.5,4,8 --out <project-dir>/out/style --width 1920 --height 1080 --fps 30
node <skill>/scripts/render.mjs --project <project-dir> --out <project-dir>/out/preview --width 1920 --height 1080 --fps 30 --start 2 --duration 4
```

按实际时长修改示例时间。该路线须暴露 `window.READY`、`window.DUR`、可重复的 `window.render(t)`，参考 assets/html-contract.html。Remotion、HyperFrames 与 Python Manim 使用自己的原生渲染入口，不强套该契约。Manim 方案在 technology 中记录 route=manim、manim_variant=manimgl 或 community。

## 6. 逐镜制作与检查

- 每镜一个主事件，次层按因果和节拍响应。运动按材质安排预备、加速/形变、接触、回稳；有目的的静止可以保留。
- 核心文字完整显现后默认至少停留 2.5 秒，长句延长；字幕按真实配音对齐，不能为了卡拍截断。
- 转场与内容关联，保持状态连续；结构节点可以有意硬切。避免默认同步淡入、全屏无差别抖动、小字堆满。
- 每镜检查起/中/末三帧，关键动作与转场查密集帧条及动态片段；只看代码不算看过画面。
- 一条时间轴驱动画面、声音事件和字幕。旁白片先落实声音时长，音乐片先测拍点/起拍偏移；整段旁白优先整段生成，长稿自然段分块须检查拼接。
- 时间确定性：浏览器逐帧路线固定种子，无墙钟/上一帧累计状态；物理用解析函数或预计算固定步长轨迹后采样；GSAP/CSS 可确定性 seek。Manim 使用原生场景顺序执行，固定种子、步长和配置，重新运行场景验证复现，不声称它能任意 render(t)。
- 字体检查覆盖本片全部中文字符；WebGL 先渲实际着色器测试帧。参考元数据的技术标签不是本机可用证明。
- 用户改配音、文字、颜色时，仅重建受影响资源和镜头；保留工程与检查点。

## 7. 导出与交付

全片前运行 `check_plan.py ... --stage render`。导出真实 MP4，再执行：

```bash
python <skill>/scripts/inspect_media.py <final.mp4> --out <project-dir>/out/media-report.json
```

核验最终文件的分辨率、帧率、时长、帧数、音轨；检查首尾、转场、阅读、黑帧/冻结/闪烁、字幕和声画同步。黑帧/停顿结合设计人工判断。能试听则试听，不能则如实说明；波形和响度不能代替试听。brief 要声音而文件无音轨时不能宣称完成。

交付 MP4、封面/关键帧拼图、按需字幕、可编辑工程、一键重建命令、导演方案与来源清单，说明实际检查及限制。仅有源码时明确是源码交付。遵循宿主持久化规则；不自动发布到第三方账号。

## 资源

- references/reference-selection.md：检索、评分、反馈与不可访问降级。
- references/stack-and-environment.md：框架分层、依赖和路线契约。
- references/directing-and-qa.md：设计、声音、时间轴和验收。
- references/sources.md、upstream-licenses.md：来源与整合边界。
- assets/project-template.json：状态与分镜模板。
- assets/catalog.json：离线参考元数据。
- assets/html-contract.html：通用逐帧渲染接口示例，不能直接当成片模板。
