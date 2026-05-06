# PROMOTE模板族索引（Layer0）

> 只管“怎么写给 SD2 更好响应”，不等于短剧风格。

## 模板族
- `T1_NARRATIVE_FLOW`：叙事流
- `T2_ACTION_TIMELINE`：动作时间轴
- `T3_SUSPENSE_EVIDENCE`：悬疑证据
- `T4_COMEDY_BEAT`：喜剧节拍

## 选择规则
- `dialogue` → `T1`
- `action` → `T2`
- `suspense` → `T3`
- `comedy` → `T4`
- `reveal` → `T2` 或 `T3`
  - 动作式揭露 → `T2`
  - 证据式揭露 → `T3`

## 结构槽位
每个模板都至少包含：
- Prefix
- Locks
- BeatMap
- BodyNarrative
- Hook

## 约束
- rendered PROMOTE 默认 ≤ 550 字
- 10 秒 CLIP 的建议预算：250–450 字
- 字数口径：中文字符数含标点
