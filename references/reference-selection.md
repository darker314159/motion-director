# 参考检索与用户选择

## 数据与刷新

参考来源包含 Skillry 在线案例库，以及 catalog.py 归一化的三个 JSON 来源：yihui 的 data/videos.json、guanmo 的 data/cases.json、Lemo 的 styleboard/catalog.json。前两个按原始 X 帖 ID 去重；Lemo 是风格/演示目录，明确标 entry_type=style。opus-video-skills 的两条实现路线在 sources.md 中按需调用，不伪造为另一个作品案例库。

刷新默认每源最多下载 8 MiB、有超时；任一源失败时保存其余结果和诊断，返回非零。读取输出的 source_status，不能把部分成功称为全量更新。可用 --yihui/--guanmo/--lemo 传入已由连接器获取的本地 JSON，从而离线归一化。禁止把第三方提示词全文写入可分发技能，只存标签和入口；研究某个选中作品时再读取原文。

案例链接失效不自动替换为“看起来相似”的虚构地址。真实 URL 才能成为来源；推断标签注明 derived_from_metadata。

## Skillry 在线案例库（联网时必查）

入口：https://skillry.dev/ai-videos/opus-5-5 。页面提供 Motion graphics、Explainers、3D scenes、Games 分类；动态图形可从已核验的 https://skillry.dev/ai-videos/opus-5-5?category=motion 开始，其他分类使用页面实际链接，不猜参数。按需求打开相关详情页；网页检索可补充 `site:skillry.dev/ai-videos/opus-5-5` 与中英主题词。只抓到首屏不能声称遍历全库。

已有 yihui JSON 的 skillry_url 同时保留为 watch_url/skillry_url，并列入 source_links；这是间接收录，不代表 Skillry 页面刚刚刷新或已观看视频。catalog.py refresh 的三个 JSON 更新与 Skillry 页面实时检索分别记录；不得用 JSON 刷新成功冒充全站同步。内置 catalog 的 gallery_sources 标明此边界。

选定候选时记录详情页、作者、原帖、已显示时长、技术标签、提示词完整/部分/未知、查阅日期和证据等级；仅保存必要元数据与链接。页面的 Original 与 Remake 是不同版本，记录实际参考版本，不能把复刻效果归给原作者；未播放不标 motion_reviewed。提示词仅在选中案例后按需读取。

以详情页 View original post 指向的 X 帖 ID 跨库合并，保留各自入口；没有原帖则使用规范化详情页 URL，并标记待去重，不能仅凭同作者合并作品。新发现案例写入项目 research/skillry-candidates.json，与 JSON 初筛结果共同重排后提供 3–5 个方向。无法访问时如实记录失败，使用已有链接/快照；不把整站计数当成已收录或已核验数。网页推荐安装的技能不自动安装。

## 检索与匹配

先扩展需求为中英词组，例如：
- 聊天教学：chat / message / conversation / UI / explainer。
- 产品宣传：product / SaaS / launch / demo / interface。
- 动态排版：kinetic / typography / Swiss / editorial。
- 2.5D：isometric / parallax / depth / orthographic。
- 玻璃/金属：glass / chrome / material / three / WebGL。

脚本词法匹配与标签分数只做可解释初筛；不是语义理解、审美评分或效果保证。无关键词匹配时明确报告 zero_matches，给放宽条件建议，不能把全库最高热度强塞成“高度匹配”。--category 是硬过滤，--duration 只给接近时长加分，未知时长不编造。

人工重排依据（各 0–5，并解释而非宣称精确测量）：任务/叙事契合 30%，运动语言 25%，信息密度与阅读 20%，风格/材质 15%，实现可行性 10%。不按相同模型名称自动加分。

## 给用户的参考卡

| 编号 | 标题/作者与播放链接 | 时长/画幅 | 建议借鉴 | 与需求差异 | 实现建议 | 核验程度 |
|---|---|---|---|---|---|---|
| A | 使用 catalog 中真实地址 | 未知则写未知 | 只描述证据支持的内容 | 需替换的内容/需简化的效果 | 一个主路线 | 见下表 |

一次 3–5 个方向；若只找到 2 个可靠案例，就给 2 个，不能凑数。参考板 HTML 只展示链接/远程封面和人工播放控件，没有自动下载或重托管媒体；用户选定编号后回到对话记录，不假装网页按钮能自动把选择发给 agent。

证据等级：
- metadata_only：只读标题/简介/技术标签；用于初筛。
- frames_reviewed：实际看过指定时间的图像；只能判断静态构图。
- motion_reviewed：看过连续片段/视频，记录片段范围；可评价运动。
- code_reviewed：读过确切工程文件，不等于已运行。
- reproduced：该实现本地运行并核验，附文件/日志证据。

这些状态独立，不能由“有源码链接”自动升级。提示词标 complete/partial/unknown 等上游状态；即使全文公开也不代表完整会话/素材已公开。code_url 可能是产品仓库而非视频场景，复用前核实具体路径。

## 用户选择后

记录主参考、辅助参考、每个借鉴维度（色彩/构图/节拍/转场/物理/相机/声音）与用户反馈原话。形成统一 DESIGN，避免“各抄一点”破坏一致性。收集不同方向前先考虑其可实现性，但不迫使用户因当前缺一个可安装包而放弃方向。

若参考打不开，可提供已核验链接供用户自己看，明确尚未观察；选择后请求上传该片或在授权范围内下载公开媒体分析。不能据标题编造运镜、音色、镜头时长。无联网时用快照和用户附件继续，说明限制。
