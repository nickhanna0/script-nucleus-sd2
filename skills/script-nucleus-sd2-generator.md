---
name: script-nucleus-sd2-generator
description: 阶段3-6生成技能。输入AdaptationPlan与原剧本（或冲突点池），输出短剧分镜（格式A/B）并执行红线校验与违规返工。保持自然语言分镜风格，适配Seedance2。内置“多尺度钩子链”检查点。
---

# script-nucleus-sd2-generator（阶段3-6）

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
