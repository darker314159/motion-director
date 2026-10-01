# 技术选型与环境

## 四层选型，不把语言、绘图库和视频框架混为一谈

| 层 | 候选 | 决策 |
|---|---|---|
| 时间轴/输出 | Remotion、HyperFrames、通用逐帧 HTML、Python Manim 原生场景 | 选择一个主时间轴，避免多套时钟互相驱动 |
| 画面 | DOM+CSS/SVG、Canvas 2D、Three.js、原生 WebGL/GLSL、p5.js（2D/WEBGL）/p5.brush、Manim Mobject | 选主画面层，可按必要性混合 |
| 动作 | 原生 frame/t 函数、GSAP 可寻址时间轴、预计算物理轨迹 | 同一时间输入得到同一画面 |
| 音频 | 用户音轨、程序合成、已授权 TTS | 跟随统一 cue 表；不自动购买服务 |

JavaScript/TypeScript 是实现语言；CSS/SVG 是表现层；Three.js 是 3D 库，WebGL 是浏览器图形 API，p5.js 是创意绘图库，Manim 是 Python 场景动画引擎；Remotion/HyperFrames 组织时间与导出。可以 Remotion+SVG 或 HyperFrames+GSAP+Three.js，但不要为了展示技术而全装。

## 路线建议

| 需求 | 优先候选 | 为什么 | 关键检查 |
|---|---|---|---|
| 聊天界面、产品教程、中文信息卡 | Remotion+React+SVG/DOM | 组件与数据组织、字幕、逐帧排版 | React/Remotion 配套版本、浏览器、字体、真实渲染 |
| HTML 多场景、字幕和已有 GSAP 设计 | HyperFrames+HTML/CSS/SVG | 组合场景与可审阅时间轴 | 实际 CLI 版本、lint/validate/inspect、编译字体 |
| 几何变形、纯代码短 MG | Canvas/SVG+确定性 JS，可配 GSAP | 层数少、自由度高、依赖较轻 | render(t)、Playwright 浏览器、FFmpeg |
| 玻璃/金属、3D 相机、复杂粒子 | Three.js/WebGL 加一个主时间轴 | 深度、材质、空间关系 | GPU/软件渲染速度、着色器、阴影、深度后期 |
| 绘本、水彩角色 | Canvas+p5/p5.brush 或匹配 Lemo 引擎 | 风格原生笔触与表演 | 每帧成本、确定性随机、角色造型 |
| 自定义着色器、程序纹理、GPU 粒子 | 原生 WebGL 1/2 + GLSL + 主时间轴 | 直接控制着色器与绘制 | 实际上下文、shader 编译/链接、像素输出、纹理尺寸/扩展；无需安装名为 webgl 的包 |
| 生成式几何、噪声、绘图 | p5.js + 2D 或 WEBGL 模式 + 主时间轴 | 创意绘图与程序图案 | p5 版本/加载、画布尺寸/密度、随机/噪声种子；WEBGL 另测 GPU；普通绘图无需 p5.brush |
| 几何推演、函数/关系图、形状变换 | Python Manim；本次参考 3b1b ManimGL | 场景对象与变换表达 | Python/venv、发行版/CLI、原生图形后端、FFmpeg、中文字体/Pango；使用 Tex 才检查 LaTeX |
| 简洁 2.5D 信息图 | SVG/Canvas+层间视差；必要时正交 Three.js | 文字清晰，控制深度成本 | 坐标转换、遮挡顺序、屏幕空间文字 |

先给一种主选和最多一种备选，说明可见效果、维护性、渲染耗时的取舍。参考选定后才锁最终框架。无 GPU 时先实测再决定是否降级；不得悄悄牺牲已确认效果。

## 依赖报告的证据边界

`doctor.py` 只做只读探测：
- Node、npm/pnpm/yarn、FFmpeg/ffprobe 命令及返回状态。
- package.json 中声明的版本和项目/运行时可解析的真实包。
- Python 的 numpy/scipy/PIL/soundfile 是否存在；ManimGL/community 发行版版本、manimlib/manim 模块、CLI 路径及常见字体/图形后端模块。范围是运行 doctor 的 Python/venv。
- 常见浏览器路径与字体工具（有无，不代表字体覆盖）。
- 执行机 OS/架构、磁盘和“仅当前环境”标识。

它不会 npx 下载，不输出环境变量、认证值或服务密钥，不运行仓库安装脚本。Node 可解析不等于浏览器已下载；需运行 `node <skill>/scripts/render.mjs --project <project> --probe` 实际启动浏览器，获得 Canvas/WebGL 探测结果。此探测不是 Three.js 场景/复杂 shader 成功证明；最终用项目自身的测试帧验证。p5 包可解析不能证明浏览器已加载；Manim 模块可发现不能证明原生图形设备可用。

本机 Windows 与 WSL 是两个环境，包和浏览器不能混为一谈。脚本兼容 Python 3 标准库；本机运行 `python scripts/doctor.py --project . --out environment.json`。远程 agent 未拿到本机结果时标记“待验证”。

## 安装与依赖固定

1. 保留项目已有包管理器及锁文件；先读 package.json 和相关说明。
2. 给出所需包、用途、命令、安装范围和下载代价。项目局部依赖属于已授权制作的正常准备；用户要求先确认安装或涉及全局修改/大模型下载/费用时再确认。
3. 不在 doctor 中执行安装。审查将要运行的上游脚本。
4. 实际版本以已安装 CLI 的 `--help` 和官方文档为准；不要在技能里硬编码 latest 永远兼容。
5. 完成所选路线的浏览器/原生渲染器启动、单帧渲染、短片编码；记录运行命令与锁定版本。

## 各路线契约

### Remotion

使用 `useCurrentFrame()`/`useVideoConfig()` 驱动动画、`Sequence` 组织镜头；相同 frame 得到相同画面。字体/素材就绪通过对应版本的异步渲染机制等待。不要另跑 rAF、CSS 自播放动画或后台 GSAP 时钟。浏览器预览成功仍需真实 renderer 测试。查阅当前官方 https://www.remotion.dev/docs/ 和宿主已安装 Remotion 技能，使用兼容版本的原生 compositions/still/render 入口。用户明确制作成片已包含导出要求。

### HyperFrames

根 HTML 指定 composition-id、宽高和 duration；按框架 data-* 定时。GSAP timeline paused 并同步注册到 `window.__timelines`；媒体由框架管理，video 静音加独立 audio。禁止无限 repeat 和等待异步回调才创建主时间轴。先静态核对最大信息量的布局，再加动画；字体按当前编译器策略嵌入并检查中文。运行当前 CLI 帮助确认命令后 lint、validate、inspect、短片 render。参考已安装 HyperFrames/CLI 技能；不要把其通用风格偏好当成本片必须的画面效果。

### 通用浏览器逐帧路线

`index.html` 暴露 `window.DUR`（秒）、`window.READY === true` 和 `window.render(t)`（同步或 Promise）。render 完成后像素就绪；其调用自身须等待必需视频 seek、GPU 或加载。设置 canvas 实际宽高与渲染 viewport 一致。每次 render 重置所有可变画面状态；随机按 seed+元素 id+时间计算，不能每调用推进 RNG。

自带 render.mjs 用本地静态服务、Playwright 截帧、FFmpeg 编码。默认禁用远程请求，字体/模块/资产落地到项目；仅经明确需要可加 --allow-remote。用 --determinism 检查乱序重绘一致性。先试 --times，再短片，最后全片；CLI 支持 --start、--duration、--audio 和 --chrome。最终音轨短于画面时补静音、长于画面时裁切，仅用于编码，不代替人工声音设计。

音频可独立 remux，不必为只改音量重绘画面。项目必须保留依赖与一键重建脚本，不能依赖技能目录里的临时下载。

### 原生 WebGL 与 p5.js

WebGL 接入主时间轴，不自建第二条实时循环。明确需要 WebGL 1 还是 2；记录实际上下文、版本、扩展/纹理限制，编译并链接本片 shader，绘制并读回像素，对最终分辨率测速度。Three.js 和 p5 WEBGL 也验证实际 GPU 路径；原生 OpenGL/WebGPU 的可用性不能由浏览器 WebGL 报告推断。

p5.js 单独作为选项，p5.brush 仅在确需笔触时追加。通用浏览器输出用 noLoop()，等待 setup/字体/素材后置 READY；以传入 t 显式更新并绘制。不要用 frameCount、millis、deltaTime 或上一帧累计值控制导出。每次评估重置 randomSeed/noiseSeed，或预计算固定轨迹；粒子和笔触历史先重建/预计算再采样。二维与 WEBGL 模式分别做测试帧，禁止把实时 draw 循环当可任意寻址的视频时间轴。

### Python Manim：轻量借鉴与可选原生路线

先参考 3b1b/manim 的 Scene/construct、Mobject/VGroup、play/wait、animate 与形状变换方法；不要求每个项目安装或搬入整个仓库，也不套用默认数学教学的字体/配色。适合几何关系、图解与变形镜头；复杂产品 UI 通常优先 DOM/SVG。只需要方法时在现有栈原创实现；选中 Python 原生制作时才检查和安装对应依赖。

明确引擎：3b1b 发行包为 manimgl，导入 manimlib，CLI 为 manimgl（上游另提供 manim-render）；社区版发行包/导入/CLI 为 manim。不能混用示例、参数、配置和安装指南。记录 technology.manim_variant 为 manimgl 或 community，固定版本/提交和 Python 虚拟环境。2026-10-01 查阅的 3b1b 主分支要求 Python >=3.10，依赖包含 wgpu/rendercanvas/glfw，README 仍有 OpenGL 说明；以所选提交依赖和实际设备测试为准，不能硬编码所有版本都需要旧版 moderngl。

先运行同一环境的 CLI --help 确认渲染参数，再做不用 Tex 的几何+中文 Text 短场景，验证字体/Pango、原生图形设备、FFmpeg 与真实输出。模块清单只说明发现情况；平台库和字体覆盖须实际渲染证明。LaTeX 是 Tex/TexText 等公式对象的条件依赖，形状/Text 无需完整 TeX 发行版。上游示例与 CLI 入口见 sources.md。

原生 Scene 以 play(..., run_time=...)、wait(...) 编排时间，合并同时发生的动画后计算总时长；锁定 fps/分辨率并核验文件。固定种子和更新步长，重新运行场景验证，不强制 window.render(t)。关键帧和 3–5 秒样片照常确认。混合项目先把 Manim 镜头渲成片段，再由主框架/FFmpeg 编排，统一帧率、尺寸、透明/背景、色彩与声画时间；不要求同时安装两套 Manim。
