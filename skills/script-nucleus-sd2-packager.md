---
name: script-nucleus-sd2-packager
description: Seedance2提示词组装技能（软约束）。输入StoryboardDoc（或分镜Markdown），输出可直接投喂Seedance2的提示词包：保持自然分镜叙事，加入可调软约束前缀、一致性声明与轻量负面约束（可开关，S/M/H档）。
---

# script-nucleus-sd2-packager（软约束PROMOTE）

## 输入
- StoryboardDoc（优先）或 rawMarkdown
- settings:
  - strength: S/M/H（默认S）
  - includeConsistencyDeclaration: true/false（默认true）
  - includeNegative: true/false（默认false）

## 输出
- 每个 CLIP 一条 prompt（自然语言为主）
- `ASSET:SeedancePromptPack` JSON

---

## 三段式软约束（不机械）
1) Prefix（短、稳定）：平台规格+影调+人物锚点+场景锚点（按档位调强度）
2) Body（长、自由）：直接复用分镜的镜1-4叙事（不强改写）
3) Guardrails（短）：仅5~8条与出片相关的轻约束（可选）

### 一致性声明（推荐开启）
- 人物外观与服装在本集保持一致
- 场景与影调保持连续
- 不新增额外人物

---

## 输出资产（必须）
```json
{
  "meta": {"type":"SeedancePromptPack","id":"pp_xxx","version":1,"status":"draft","createdAt":0,"updatedAt":0,"title":"SD2 Prompt Pack"},
  "sourceStoryboardId": "sb_xxx",
  "policy": {"strength":"S","includeConsistencyDeclaration":true,"includeNegative":false},
  "global": {"prefix":"","consistencyDeclaration":"","negative":""},
  "items": [{"id":"s1e01_c01","durationSec":10,"prompt":""}]
}
```
