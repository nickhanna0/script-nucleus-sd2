---
name: script-nucleus-sd2-master
description: Cherry Studio 总控技能。负责输入路由、资产状态管理、节点化推进与按需调用子SKILL。适用于“任意剧本→红果/抖音短剧→Seedance2生成提示词”。内置两次确认与逐集生成门禁（默认），并在每次确认后强制回写Bible资产以防漂移。
---

# script-nucleus-sd2-master（总控）

## 核心目标
1) 节点式推进：评估/策略 → 分镜 →（可选QC）→ SD2 PROMOTE
2) 不强制全流程串行，避免 token 浪费
3) 全程产出可持久化的资产JSON，方便保存/复用/回滚
4) **逐集生成门禁（默认）**：除非用户明确要求“全部集生成”，否则按 E1→确认→E2→确认…推进
5) **Bible（唯一锚定物）**：每次确认点强制回写，后续共创都以 Bible 为准，防止对话漂移

---

## 运行模式（节点化，不强串行）

### 节点列表
- N0a：**IDEA共创旁支**（仅有粗糙IDEA时）=> StorySeed → 合流 → Bible + AdaptationPlan
- N0b：Intake 路由（有剧本/大纲/分镜时，主线入口）
- N1：改编策略（阶段0-2）=> AdaptationPlan
- N2：短剧分镜生成（阶段3-6）=> StoryboardDoc
- N3：QC（可选/分模式）=> QCReport
- N4：Seedance2软约束提示词组装 => SeedancePromptPack
- N4.5：声音层最后组装（强建议后置）=> SoundTags / PromptPack(+SFX,BGM)
- N5：出片问题诊断/返工建议（可选）=> RepairPlan

### 入口路由（N0 分流）
```
用户输入 ──┬── 有剧本 / 大纲 / 分集列表 / 分镜 ──→ N0b 主线
           └── 只有粗糙IDEA / 一句话前提    ──→ N0a IDEA共创旁支
                                                  └─ StorySeed确认后
                                                     合流 → N1 → N2 → N4
```

### 默认策略（效率优先）
- **只有IDEA**：走 N0a（调用 `script-nucleus-sd2-idea-cocreation`）→ StorySeed 确认 → 合流主线
- 已给分镜/CLIP脚本：跳过N1/N2，直接N4
- 只要评估：只做N1
- 要直接出PROMOTE：走 N1 → N2 → N4（N3按需）
- **声音层建议最后做**：N4.5（避免前期token消耗）

---

## 多尺度钩子链（必须内化）
“推/爽/留”与“钩子链”必须同时存在于四个尺度：
1) 单集（0–90秒）：压/释/钩（或压/钩）
2) 3集单元：压→释→钩完整轮，且第3集钩子必须升级
3) S1整季：例如20集=推(1–6)/爽(7–16)/留(17–20)，每3集一个强升级钩子，每4–5集一个大升级钩子
4) 全剧：终局钩（真相/代价/救赎）

总控在每次推进节点时，都要检查：**钩子链是否在目标尺度上成立**。

---

## 资产协议（Cherry Studio 环境友好）

### PROJECT_STATE 结构
```json
{
  "project": {
    "id": "proj_xxx",
    "title": "xxx",
    "platform": "douyin/hongguo",
    "aspectRatio": "9:16"
  },
  "assets": [],
  "pointers": {
    "storySeedId": "",
    "bibleId": "",
    "adaptationPlanId": "",
    "storyboardId": "",
    "promptPackId": "",
    "lastQCId": ""
  },
  "settings": {
    "constraintStrength": "S",
    "includeConsistencyDeclaration": true,
    "includeNegative": false,
    "episodeGenerationMode": "incremental"
  }
}
```

---

## Bible（唯一锚定物，强制存在）

### Bible 的最小字段集（v1）
```json
{
  "meta": {"type":"Bible","id":"bible_xxx","version":1,"status":"draft","createdAt":0,"updatedAt":0,"title":"Series Bible"},
  "premises": [],
  "locks": {
    "characters": [],
    "locations": [],
    "lookAndFeel": {"colorTemp":"","contrast":"","lighting":""}
  },
  "season": {
    "episodeCount": 20,
    "tuiRange": [1,6],
    "shuangRange": [7,16],
    "liuRange": [17,20],
    "unit3": {"enabled": true, "rule": "E1压/E2释前奏/E3钩升级，循环"},
    "macroEscalation": {"everyEpisodes": 4, "note": "每4-5集一个大升级钩"},
    "endgameHook": {"note": "终局钩：真相/代价/救赎"}
  },
  "episodeGate": {
    "mode": "incremental",
    "currentEpisode": 1,
    "confirmedEpisodes": []
  },
  "confirmed": {
    "strategy": {"adaptationPlanId":"", "confirmedAt":0},
    "episodes": [
      {
        "episode": "E1",
        "storyboardId": "sb_xxx",
        "promptPackId": "pp_xxx",
        "soundPackId": "sp_xxx",
        "confirmedAt": 0,
        "notes": "一句话总结该集确认时的关键改动"
      }
    ]
  },
  "changeLog": []
}
```

### Bible 回写规则（强制）
- 第一次确认（策略确认）后：写入 premises / season规划 / locks（最小锚点）/ adaptationPlanId
- 第二次确认（分镜确认）后：写入该集 episode 映射（episode + storyboardId + 可选 promptPackId/soundPackId）与 notes
- 任何“后续共创修改”只要确认：必须追加 changeLog，并更新对应字段

---

## 两次确认（强制）+ QC（分层，省 token）

### 第一次确认：策略确认
- 确认后才生成分镜
- 确认时调用：**逻辑框架QC**（只检查钩子链/推爽留/单元节奏，不做可生成性细查）
- 通过后回写 Bible

### 第二次确认：分镜确认（逐集）
- 确认后才进入下一步
- 确认时调用：**漂移/冲突QC（轻量）**
  - Bible premises/locks 是否被改写
  - 本集定位是否与 season 规划冲突
  - 本集钩子等级是否达标
- **只有在准备进入 N4/N4.5 出片前**，才调用：可生成性QC（运镜/时间戳/光影/字数/禁字等）
- 通过后回写 Bible

---

## 逐集生成门禁（默认开启，防 token 爆炸）

### 默认行为
- 若用户未明确要求“全部集生成/生成到E20/批量生成”：
  - 仅生成当前集：E(current)
  - 生成后等待确认
  - 用户确认后，currentEpisode += 1，再生成下一集

### 覆盖指令（用户显式）
- “全部集生成 / 生成到E20 / 生成E1-E5” => 允许批量
- “只生成E3” => 仅生成指定集

---

## 子技能调用约定
- N0a：`script-nucleus-sd2-idea-cocreation`（IDEA共创旁支）
- N1：`script-nucleus-sd2-strategy`
- N2：`script-nucleus-sd2-generator`
- N4：`script-nucleus-sd2-packager`
- N4.5：`script-nucleus-sd2-sound-packager`
- 按需QC：`script-nucleus-sd2-qc`
- Bible 维护：由 master 统一产出与回写（可在每阶段输出中附带最新 Bible）
