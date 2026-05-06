# script-nucleus-sd2 架构说明

## 目标
面向短剧改编与 Seedance2 出片的分阶段工作流，支持：长剧本改编、IDEA共创细化、分镜生成、提示词组装、声音层补充、QC 返工、逐集确认回写。

---

## 两条入口路由

```
用户输入
  ├─ 有剧本 / 大纲 / 分集列表 / 分镜
  │    └─ N0b 主线 ─→ N1 Strategy ─→ N2 Generator ─→ N4 Packager …
  │
  └─ 只有粗糙IDEA（一句话前提）
       └─ N0a IDEA共创旁支 ─→ StorySeed确认
                                  └─ 合流 ─→ N1 Strategy ─→ N2 Generator ─→ N4 Packager …
```

### 主线（N0b）
适用于：有现成剧本、大纲、分集列表或分镜文档。  
资产链：`AdaptationPlan → Bible → StoryboardDoc → SeedancePromptPack`

### IDEA共创旁支（N0a）
适用于：用户只有一句话IDEA，需要通过对话细化到可执行的宏观结构。  
旁支在**季宏观结构层（L3_MACRO）停止**，确认后合流进入主线。  
资产链：`StorySeed → Bible（初始化）+ AdaptationPlan（简化）→ 合流主线`

---

## 节点说明

| 节点 | 技能文件 | 输入 | 输出 |
|------|---------|------|------|
| N0a | `idea-cocreation` | 粗糙IDEA | StorySeed |
| N0b | — | 剧本/大纲 | 路由分流 |
| N1 | `strategy` | 剧本/大纲 or StorySeed合流 | AdaptationPlan + Bible |
| N2 | `generator` | AdaptationPlan + Bible | StoryboardDoc（逐集）|
| N3 | `qc` | StoryboardDoc / PromptPack | QCReport + RepairPlan |
| N4 | `packager` | StoryboardDoc | SeedancePromptPack |
| N4.5 | `sound-packager` | StoryboardDoc / PromptPack | SoundTags + SoundPack |
| N5 | `qc`（诊断模式）| 失败视频反馈 | RepairPlan |

---

## 核心资产

| 资产 | 说明 | 创建时机 |
|------|------|---------|
| `StorySeed` | IDEA共创旁支输出；含原始IDEA/Q&A/主题/人物弧/冲突/季规划/分集草稿 | N0a完成并确认时 |
| `Bible` | 唯一真值源；所有确认结果必须回写 | N0a合流或N1策略确认后 |
| `AdaptationPlan` | 改编策略（季规划/推爽留/钩子链） | N1策略确认后 |
| `StoryboardDoc` | 逐集分镜（逐集逐步生成） | N2每集确认后 |
| `SeedancePromptPack` | Seedance2 PROMOTE提示词包 | N4 |
| `SoundPack` | SFX/BGM关键词声音层 | N4.5（后置） |
| `QCReport` | QC报告与最小返工建议 | N3/N5 |

---

## Bible 回写规则（强制）
- **StorySeed确认（N0a）** → 写入 premises / season / locks（用StorySeed数据初始化）
- **策略确认（N1）** → 写入/更新 premises / season / locks / adaptationPlanId
- **分镜确认（N2，逐集）** → 追加 `confirmed.episodes[]`（storyboardId / notes）
- **任何修改确认** → 追加 changeLog

---

## QC 分层（省 token）

| 触发时机 | QC模式 | 检查重点 |
|---------|-------|---------|
| 策略确认 / StorySeed确认 | 逻辑框架QC（轻）| 四尺度钩子链、推爽留分段、单元节奏 |
| 分镜确认（逐集）| 漂移/冲突QC（轻）| Bible premises/locks是否被改写；本集钩子是否达标 |
| 出片前（N4/N4.5）| 可生成性QC（重）| 运镜/一镜一动/时间戳/光影/字数/禁字水印等 |

---

## 逐集门禁（默认）
- 默认：E1 → 确认 → E2 → 确认 … （防 token 爆炸）
- 用户明确说"批量生成/全部集"才允许批量
- 每集确认后回写 Bible `confirmed.episodes[]`

---

## 多尺度钩子链（必须四层同时成立）
1. 单集（0–90s）：压 / 释 / 钩
2. 3集单元：压 → 释 → 钩；第3集钩子必须升级
3. S1整季：推(1–6) / 爽(7–16) / 留(17–20)；每3集强升级钩，每4–5集大升级钩
4. 全剧：终局钩（真相 / 代价 / 救赎）

---

## 省 token 策略总结
- N0a 共创问答最多 3 轮
- 旁支只到L3_MACRO（季宏观），不展开单集细节
- 分镜逐集生成，不默认批量
- 确认点只做轻量QC；可生成性重QC延迟到出片前
- 声音层（N4.5）后置
