---
name: script-nucleus-sd2-sound-packager
description: 短剧声音层最后组装技能。仅在CLIP内容（分镜/提示词主体）确认后调用，为每个CLIP生成极简SFX与BGM关键词，并按需把声音标签拼接进Seedance2 PROMOTE（可开关）。目标：减少前期token消耗、让画面先定型、声音最后自适应。
---

# script-nucleus-sd2-sound-packager（声音最后组装）

## 适用时机（强建议）
- **只在**用户已确认：分镜/CLIP内容（镜头与台词）之后调用
- 作为 PROMOTE 的最后一道工序：对每个CLIP补齐声音关键词

这样能：
- 前期 token 聚焦画面与剧情
- 声音设计基于“已定型CLIP”，更贴合情绪与卡点

---

## 输入
- StoryboardDoc（优先）或 SeedancePromptPack（二选一即可）
- settings:
  - attachToPromote: true/false（默认false）
    - false：只输出声音标签（推荐，用于后期剪辑/人工混音）
    - true：把 `SFX:` `BGM:` 两行追加到每条 prompt 末尾（实验用）
  - density: "lite" | "normal"（默认lite）
    - lite：SFX 2-4个关键词；BGM 1个关键词（允许“无声/留白”）
    - normal：SFX 3-6个关键词；BGM 2个关键词（仍需短）

---

## 输出
- 每个CLIP两行：
  - `SFX:` 用 `｜` 分隔关键词
  - `BGM:` 1-2个关键词（允许“无声/留白/低频氛围/骤停”）
- 若 attachToPromote=true：输出更新后的 SeedancePromptPack（同 id，新 version）

---

## 自适应判断规则（必须内化）
### 1) 压抑/禁忌/羞耻/威胁
- **优先：无声/低频氛围**
- 放大微声：呼吸、吞咽、布料、指尖、手机震动、心跳（可选）

### 2) 爽点释放/反击/打脸
- BGM：鼓点上扬/短促重击/快切节奏
- SFX：脚步、摔物、拍桌、拉椅、关门（按画面）

### 3) 钩子/反转/危机降临
- BGM：一记低音重击 或 **骤停留白**
- SFX：来电、提示音、门铃、敲门、刹车、金属响

### 4) 呼吸感
- 避免“全程铺满BGM”。若画面主打眼神拉扯，允许整段无声。

---

## 输出模板
```text
CLIP s1e01_c01
SFX: 安全带咔哒｜手机轻震｜呼吸停顿
BGM: 无声/低频氛围
```
