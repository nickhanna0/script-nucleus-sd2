---
name: script-nucleus-sd2-qc
description: Seedance2友好QC与返工建议。输入StoryboardDoc或PromptPack以及用户对生成视频的反馈，输出漂移风险、可生成性问题、以及最小改动返工建议（不需要重做全套）。
---

# script-nucleus-sd2-qc

## 输入
- StoryboardDoc / SeedancePromptPack
- 用户反馈（失败类型）：如“角色变脸”“镜头没快切”“动作太僵硬”“场景漂移”“出现文字水印”
- 可选：用户提供生成视频截图/描述

## 输出
- QCReport（问题分类 + 严重级别）
- RepairPlan（最小改动策略：改前缀/改声明/改某CLIP几句/升档位S→M等）

---

## Layer0 v2 执行卡引用（检查依据）
- 统一入口：`kb/layer0/index.md`
- 运镜与镜头语言：`kb/layer0/camera-motion-rules.md`
- 描述性优先：`kb/layer0/descriptive-vs-narrative.md`
- 时间戳切片：`kb/layer0/timestamp-blocking.md`
- 三层光影：`kb/layer0/light-structure.md`

---

## 最小改动优先级（从低到高）
1) 仅增强一致性声明（不改正文）
2) S→M（加强人物/场景锚点短句）
3) 对单个CLIP的镜1-4做局部改写（不动其他CLIP）
4) 返回generator阶段4/5局部返工

---

## 快速检查清单（新增 v2）

### A. 运镜与镜头规则
- 裸英文运镜词（Dolly/Aerial/Crane/Pan/Arc/Dutch/Steadicam）是否出现？（应改为中文或英文完整短语）
- 是否违反“一镜一动”：同一时间切片内叠加多个强动作源（主体大运动 + 镜头环绕/摇臂/推拉混用）？
- 运镜是否过度堆叠导致执行困难？（建议减到 1 个）

### B. 描述性优先
- 是否出现大量抽象心理词：感到/觉得/内心/崩溃/愤怒/绝望（缺少可见细节支撑）？
- 是否能用 1–2 个可见细节替换抽象情绪？

### C. 时间戳切片与节拍
- 10s 以上或动作密度高的 CLIP 是否提供切片节拍？
- 最后 1–3 秒 hook 是否明确、可视化？（脚步/来电亮屏/证据翻到关键页等）

### D. 光影可执行性
- 是否只有“高级/氛围/电影感”而缺少可执行的光源/光行为/色调？
- dialogue 类是否光影过长挤占表情细节？

### E. 通用渲染风险
- 是否出现文字/字幕/LOGO/水印？（应显式禁止）
- rendered 是否超过 550 字？（超限按 packager 裁剪策略处理）
