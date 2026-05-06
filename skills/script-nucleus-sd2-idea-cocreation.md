---
name: script-nucleus-sd2-idea-cocreation
description: IDEA共创旁支技能。用户仅有粗糙IDEA（一句话前提）时使用。通过对话问答细化IDEA，输出StorySeed资产（含主题/人物弧/冲突/季规划/分集草稿）。StorySeed确认后合流到主线，写入Bible与AdaptationPlan，再进入N1 Strategy及后续流程。主线（有剧本/大纲/分镜时）不需要调用本技能。
---

# script-nucleus-sd2-idea-cocreation（IDEA共创旁支）

## 适用场景
- 用户只有一句话IDEA / 粗糙前提，**没有**现成剧本、大纲或分集列表
- 用户希望通过对话细化IDEA，最终输出可执行的短剧宏观结构
- 主线入口（N0b，有现成剧本/大纲）**不需要**本技能

## 旁支与主线的关系
```
用户IDEA
  └─ N0a: IDEA共创旁支
       ├─ 共创问答（本技能）
       ├─ 输出 StorySeed
       ├─ StorySeed确认 → 写入 Bible + AdaptationPlan
       └─ 合流 → N1 Strategy → N2 Generator → N4 Packager …
```

---

## 共创流程（三轮问答，省 token）

### 第一轮：核心理解
向用户提问（最多 3 个问题，不超过 1 轮）：
1. 这个故事最想让观众感受到什么？（主题 / 情感内核）
2. 主角是谁？她/他面对什么困境或欲望？（人物弧起点）
3. 最核心的冲突是什么？（内部 vs 外部；关系 vs 系统）

### 第二轮：结构确认
根据第一轮答案，给出初步框架草稿：
- 核心概念（一句话精炼）
- 主角弧线（起点 → 转折 → 终点）
- 主冲突类型
- 建议集数与推爽留分段

向用户确认："这个方向对吗？有需要调整的吗？"

### 第三轮：分集草稿
输出每3集一个单元的分集草稿（列表形式，不超过 5 行/单元）：
- 列出各单元的关键事件与集尾钩
- 标出终局钩（真相 / 代价 / 救赎）

---

## 确认点（StorySeed确认）
当用户确认草稿（"通过 / OK / 继续"）时：
1. 触发 **逻辑框架QC**（同策略确认点，检查钩子链/推爽留/单元节奏）
2. 通过后输出 `ASSET:StorySeed`
3. 同步写入 / 初始化 `ASSET:Bible`（premises / locks / season）
4. 同步输出 `ASSET:AdaptationPlan`（可简化版）
5. 通知用户：**"StorySeed 已确认，可进入主线生成分镜（N2 Generator）"**

---

## 输出资产：StorySeed

```json
{
  "meta": {
    "type": "StorySeed",
    "id": "ss_xxx",
    "version": 1,
    "status": "draft",
    "createdAt": 0,
    "updatedAt": 0,
    "title": "Story Seed"
  },
  "originalIdea": "用户原始一句话IDEA",
  "coCreationLog": [
    {"round": 1, "question": "...", "answer": "..."},
    {"round": 2, "question": "...", "answer": "..."},
    {"round": 3, "question": "...", "answer": "..."}
  ],
  "refinedConcept": "精炼后的核心概念（一句话）",
  "theme": {
    "core": "主题内核",
    "moralUplift": "道德升华 / 情感共鸣点"
  },
  "characterArcs": [
    {
      "id": "A",
      "name": "",
      "arcStart": "起点状态",
      "arcTurning": "关键转折",
      "arcEnd": "终点状态"
    }
  ],
  "storyCore": {
    "conflictType": "内部/外部/关系/系统",
    "centralConflict": "核心冲突一句话描述",
    "stakes": "代价是什么"
  },
  "seasonMacro": {
    "episodeCount": 20,
    "tuiRange": [1, 6],
    "shuangRange": [7, 16],
    "liuRange": [17, 20],
    "unit3": {"enabled": true, "rule": "E1压/E2释前奏/E3钩升级，循环"},
    "macroEscalation": {"everyEpisodes": 4, "note": "每4-5集一个大升级钩"},
    "endgameHook": {"note": "终局钩：真相/代价/救赎"}
  },
  "episodeDraft": [
    {
      "unit": "U1",
      "episodes": [1, 2, 3],
      "keyEvents": "单元关键事件摘要",
      "unitEndHook": "单元末集尾钩（LV2+）"
    }
  ]
}
```

---

## 合流规则（StorySeed → 主线）

StorySeed 确认后，本技能负责输出：

| 资产 | 来源 | 说明 |
|------|------|------|
| `Bible` | 由 StorySeed 初始化 | premises 来自 refinedConcept + theme；season 来自 seasonMacro |
| `AdaptationPlan` | 由 StorySeed 简化生成 | season / premises 字段与 StorySeed 对齐 |

初始化后，主线可正常使用 Bible 与 AdaptationPlan 进入：
- N2 Generator（生成分镜）
- N4 Packager（组装 PROMOTE）
- N3 QC（按需）

---

## 约束
- 共创问答**最多 3 轮**，避免 token 爆炸
- 分集草稿**只到宏观单元级别**（L3_MACRO，不展开到单集细节）
- 单集细节由 N2 Generator 逐集生成（受逐集门禁约束）
- 本技能不负责分镜、PROMOTE、声音层
