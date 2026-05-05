---
name: script-nucleus-sd2-packager
description: Seedance2提示词组装技能（软约束）。输入StoryboardDoc（或分镜Markdown），输出可直接投喂Seedance2的提示词包：保持自然分镜叙事，加入可调软约束前缀、一致性声明与轻量负面约束（可开关，S/M/H档）。支持“字段化组件 + 渲染成可复制PROMOTE”，并对渲染PROMOTE做长度约束以避免注意力稀释。
---

# script-nucleus-sd2-packager（软约束PROMOTE）

## 输入
- StoryboardDoc（优先）或 rawMarkdown
- settings:
  - strength: S/M/H（默认S）
  - includeConsistencyDeclaration: true/false（默认true）
  - includeNegative: true/false（默认false）
  - outputMode: "components+rendered" | "components" | "rendered"（默认"components+rendered"）
  - renderMaxChars: 550（默认550；仅约束 rendered 文本）
  - renderCharCounting: "A"（默认A：按中文字符数含标点；口径固定避免歧义）

> 约束说明：**字段化 components 不受 renderMaxChars 限制**；只有可复制的 rendered PROMOTE 必须 ≤ renderMaxChars。

## 输出
- 每个 CLIP 一条 prompt（可复制，长度受控）
- 同时输出 PROMOTE 字段化组件（可审稿/可局部修改）
- `ASSET:SeedancePromptPack` JSON（包含 components 与 rendered）

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

## PROMOTE 模板族（写作结构 ≠ 短剧风格）
> 注意：PROMOTE 模板用于提升 Seedance2 的可执行性，与“短剧风格卡（题材/受众预期）”是不同维度。

建议至少支持 4 个模板（上限 4，避免系统臃肿）：
- **T1 叙事流（Narrative-Flow）**：适合文戏/情绪对峙/暧昧拉扯
- **T2 动作时间轴（Action-Timeline）**：适合武戏/动作/高密度冲突
- **T3 悬疑证据（Suspense-Evidence）**：适合线索/证据推进（强调遮挡与不展示可读文字）
- **T4 喜剧节��（Comedy-Beat）**：适合反差梗点（setup→misdirect→punchline→aftertaste）

模板选择建议（按 CLIP_TYPE，而非按风格）：
- dialogue → T1
- action → T2
- suspense → T3
- comedy → T4
- reveal → T2 或 T3（看是“动作揭露”还是“证据揭露”）

---

## 字段化组件（components）+ 渲染（rendered）双输出

### components 字段建议
每个 CLIP 输出一份结构化组件，便于：
- 只改人物锚点/场景锚点，不动正文
- 只改节拍，不重写整段
- 只改钩子，不影响镜头执行

组件最小字段集（示例）：
- Prefix（1-2行）
- Locks（人物/场景/连续性声明）
- BeatMap（0-3 / 3-6 / 6-9 / 9-10 的事件节拍词 + 镜头提示）
- BodyNarrative（主体叙事文本，允许留白）
- Hook（最后一帧+结束方式+钩子等级）

### rendered 渲染规则（固定拼装顺序）
渲染为“可复制PROMOTE文本”时，按顺序拼装：
1) Prefix（必要时压缩为 1 行）
2) 一致性声明（压缩为 1-2 条短句）
3) BodyNarrative（优先保留 BeatMap 关键动作与情绪点）
4) Hook（最后一帧/定格/黑屏一句）

---

## rendered 长度硬约束：≤ 550 字（默认）
> 目的：避免 Seedance2 注意力稀释。

### 超限裁剪策略（从低价值到高价值，逐级裁剪）
1) 先删/压缩 Guardrails（若存在）
2) Prefix 压到 1 行
3) 一致性声明压到 1-2 条
4) 最后才压缩 BodyNarrative（保留：动作/空间关系/情绪点/钩子）

---

## 输出资产（更新：包含 components 与 rendered）
```json
{
  "meta": {"type":"SeedancePromptPack","id":"pp_xxx","version":2,"status":"draft","createdAt":0,"updatedAt":0,"title":"SD2 Prompt Pack"},
  "sourceStoryboardId": "sb_xxx",
  "policy": {
    "strength":"S",
    "includeConsistencyDeclaration":true,
    "includeNegative":false,
    "outputMode":"components+rendered",
    "renderMaxChars":550,
    "renderCharCounting":"A"
  },
  "global": {"prefix":"","consistencyDeclaration":"","negative":""},
  "items": [
    {
      "id":"s1e01_c01",
      "durationSec":10,
      "template":"T1",
      "components": {"prefix":[],"locks":{},"beatMap":[],"bodyNarrative":"","hook":{}},
      "rendered":""
    }
  ]
}
```
