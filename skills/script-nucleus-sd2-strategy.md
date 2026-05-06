---
name: script-nucleus-sd2-strategy
description: 阶段0-2策略技能。输入长剧本/长大纲后，完成：输入评估、冲突密度重组、阶段判定与策略制定。输出工程化AdaptationPlan资产，用于后续生产。默认在策略确认后触发一次“逻辑框架QC”，并回写Bible作为唯一锚定物。
---

# script-nucleus-sd2-strategy（阶段0-2）

## 输入
- 原剧本/大纲（可长文本）
- 可选：平台（抖音/红果）、目标集数（默认20）、每集时长（默认60-90秒）
- 可选：Bible（若已存在，以 Bible 为准，避免漂移）

## 输出
- 策略摘要
- 冲突点提取统计（默认Top 15，避免token爆炸）
- **多尺度钩子链设计**（单集/3集/S1/全剧）
- `ASSET:AdaptationPlan` JSON
- （推荐）`ASSET:Bible` JSON（策略确认后回写：premises/season/locks）

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
- 终局钩说明（endgame hook note）

---

## 策略确认点（新增：Bible 回写）
当用户对策略确认（“通过/OK/继续生成分镜”）时：
1) 触发一次 QC（逻辑框架检查）：检查钩子链、推爽留分段、单集/3集/S1/全剧四尺度是否冲突
2) 通过后回写 Bible：固化 premises/season/locks/adaptationPlanId

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
    "macroEscalation": {"everyEpisodes": 4, "note": "每4-5集一个大升级钩"},
    "endgameHook": {"note": "终局钩：真相/代价/救赎"}
  },
  "intake": {"wordCount":0,"sceneCount":0,"majorCharacters":[],"complexity":"linear|multi|web","genre":"","styleTendency":"","emotionalTone":"","score":0,"recommendation":"full|extract|rebuild"},
  "conflictRecomposition": {"extractedCount":0,"transformNeededCount":0,"distribution":{"qi":0,"cheng":0,"zhuan":0,"he":0},"templates":[],"newConflictsNeeded":0,"conflicts":[]},
  "strategy": {"phase":"qi|cheng|zhuan|he|mixed","psyLayer":"tui|shuang|liu|mixed","pacing":"","hookDensity":"","templateUsage":"","dialogueStyle":""}
}
```

---

## Bible 最小资产（v1，策略阶段可初始化/更新）
```json
{
  "meta": {"type":"Bible","id":"bible_xxx","version":1,"status":"draft","createdAt":0,"updatedAt":0,"title":"Series Bible"},
  "premises": [],
  "locks": {"characters": [], "locations": [], "lookAndFeel": {"colorTemp":"","contrast":"","lighting":""}},
  "season": {
    "episodeCount": 20,
    "tuiRange": [1,6],
    "shuangRange": [7,16],
    "liuRange": [17,20],
    "unit3": {"enabled": true, "rule": "E1压/E2释前奏/E3钩升级，循环"},
    "macroEscalation": {"everyEpisodes": 4, "note": "每4-5集一个大升级钩"},
    "endgameHook": {"note": "终局钩：真相/代价/救赎"}
  },
  "episodeGate": {"mode": "incremental", "currentEpisode": 1, "confirmedEpisodes": []},
  "confirmed": {"strategy": {"adaptationPlanId":"", "confirmedAt":0}, "episodes": []},
  "changeLog": []
}
```
