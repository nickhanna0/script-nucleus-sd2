---
name: script-nucleus-sd2-strategy
description: 阶段0-2策略技能。输入长剧本/长大纲后，完成：输入评估、冲突密度重组、阶段判定与策略制定。输出工程化AdaptationPlan资产，用于后续生成器。内化“推爽留多尺度嵌套（钩子链）”。
---

# script-nucleus-sd2-strategy（阶段0-2）

## 输入
- 原剧本/大纲（可长文本）
- 可选：平台（抖音/红果）、目标集数（默认20）、每集时长（默认60-90秒）

## 输出
- 策略摘要
- 冲突点提取统计（默认Top 15，避免token爆炸）
- **多尺度钩子链设计**（单集/3集/S1/全剧）
- `ASSET:AdaptationPlan` JSON

---

## 必须内化：推爽留多尺度嵌套（钩子链）
推/爽/留不是单一层级概念，必须同时落在：
1) 单集（0–90s）：压/释/钩
2) 3集单元：压→释→钩（第3集钩子升级）
3) S1整季分段：例如20集=推(1–6)/爽(7–16)/留(17–20)
4) 全剧：终局钩（真相/代价/救赎）

策略阶段必须输出：
- S1分段（tui/shuang/liu ranges）
- 每3集升级点（unit3 cadence）
- 每4–5集大升级点（macro escalation）

---

## 片段输入的世界观/弧光/分季规则（防脑补污染）
若用户只给“片段”，不得凭空扩写大世界观；但必须给出“最小可用骨架”以支撑分集：
- 现实题材默认：都市职场/家庭
- S1集数：按用户目标（默认20）
- 弧光：仅给主角与对手各1条（可调整）
- 关系/秘密：以用户确认的 premises 为准

---

## 输出资产（必须）
```json
{
  "meta": {"type":"AdaptationPlan","id":"ap_xxx","version":1,"status":"draft","createdAt":0,"updatedAt":0,"title":"Adaptation Plan"},
  "premises": ["...用户确认的关键设定..."],
  "season": {
    "episodeCount": 20,
    "tuiRange": [1,6],
    "shuangRange": [7,16],
    "liuRange": [17,20],
    "unit3": {"enabled": true, "rule": "E1压/E2释前奏/E3钩升级，循环"},
    "macroEscalation": {"everyEpisodes": 4, "note": "每4-5集一个大升级钩"}
  },
  "intake": {"wordCount":0,"sceneCount":0,"majorCharacters":[],"complexity":"linear|multi|web","genre":"","styleTendency":"","emotionalTone":"","score":0,"recommendation":"full|extract|rebuild"},
  "conflictRecomposition": {"extractedCount":0,"transformNeededCount":0,"distribution":{"qi":0,"cheng":0,"zhuan":0,"he":0},"templates":[],"newConflictsNeeded":0,"conflicts":[]},
  "strategy": {"phase":"qi|cheng|zhuan|he|mixed","psyLayer":"tui|shuang|liu|mixed","pacing":"","hookDensity":"","templateUsage":"","dialogueStyle":""}
}
```
