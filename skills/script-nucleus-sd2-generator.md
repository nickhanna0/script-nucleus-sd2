---
name: script-nucleus-sd2-generator
description: 阶段3-6生成技能。输入AdaptationPlan与原剧本（或冲突点池），输出短剧分镜（格式A/B）并执行红线校验与违规返工。保持自然语言分镜风格，适配Seedance2。内置“多尺度钩子链”检查点，并给出渲染PROMOTE的字数预算以减少后续裁剪。
---

# script-nucleus-sd2-generator��阶段3-6）

## 输入
- AdaptationPlan（来自 strategy）
- 原剧本/片段（可选，若 plan 已含冲突点池可减少重复）
- 生成目标：S1集数、每集时长、CLIP时长（默认10s）
- 约束强度（S/M/H，用于锁定文本强度，默认S）

## 输出
- Storyboard Markdown（格式A/B）
- `ASSET:StoryboardDoc` JSON（含 rawMarkdown）
- 若违规：返回 {状态: 返回, 返回阶段: 3/4/5, 违规清单, 重写次数}

---

## 必须内化：多尺度钩子链（不得在推段变平）
即便处于“推段”（S1前段），也必须：
- 每集：集尾钩 ≥ LV2（悬念/危机/反转/曝光风险）
- 每3集：第3集钩子必须升级（筹码更大、第三方介入、证据更明确）
- 每4–5集：必须有一次“大升级钩”（宏观推进，不可原地踏步）

---

## 渲染PROMOTE字数预算（用于减少后续packager裁剪）
> 目标：分镜阶段就控制“可复制PROMOTE”的信息密度，避免过短导致情绪不到位，也避免过长导致Seedance2注意力稀释。

### 口径
- 以“中文字符数（含标点）”为口径。

### 默认预算（10秒CLIP）
- **建议范围：250–450字**（不强制，但超出应提醒/自压缩）
  - 低于250字：易出现情绪不到位/台词被压缩过度/动作空间关系不清
  - 高于450字：后续渲染≤550字时容易被裁剪伤到关键动作

### 预算使用建议
- 优先写清：动作/空间关系/关键表情/卡点钩子
- 台词尽量短句（≤20字），但允许用“无声/停顿/吞咽”等补情绪
- 若是动作/武戏CLIP（高密度卡点），可把更多字数分配给节拍动作，而减少心理描写

---

## Layer0 v2 执行卡引用（必须遵守）
- 统一入口：`kb/layer0/index.md`
- 运镜与镜头语言：`kb/layer0/camera-motion-rules.md`
- 描述性优先：`kb/layer0/descriptive-vs-narrative.md`
- 时间戳切片：`kb/layer0/timestamp-blocking.md`
- 三层光影：`kb/layer0/light-structure.md`

生成分镜时：
- 优先输出“可见细节”而非抽象心理判断（参考描述性优先执行卡）
- 对 10s 以上或高密度动作 CLIP，推荐用时间戳切片写法
- 遵守“一镜一动”，避免同切片叠加两个强运动源

---

## 生成偏好（Seedance2友好，避免机械）
- 分镜保持自然语言叙事，不强拆镜头prompt
- 允许少量留白，让模型发挥微表情与过渡
- 但必须提供：人物锚点、场景锚点、影调锚点（短句即可）

---

## 输出资产骨架（必须）
```json
{
  "meta": {"type":"StoryboardDoc","id":"sb_xxx","version":1,"status":"draft","createdAt":0,"updatedAt":0,"title":"Storyboard"},
  "format": "CLIP_STANDARD|NARRATIVE_FLOW",
  "overview": {"episodeCount":0,"totalDurationSec":0,"strategySummary":""},
  "locks": {
    "globalPrefix": "",
    "characters": [{"id":"A","name":"","lockText":""}],
    "locations": [{"id":"LOC1","name":"","lockText":""}],
    "lookAndFeel": {"colorTemp":"","contrast":"","lighting":""}
  },
  "episodes": [],
  "rawMarkdown": ""
}
```
