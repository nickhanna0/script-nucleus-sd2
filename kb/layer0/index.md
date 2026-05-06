# Layer0 索引（v1 + v2）

> 目的：给 skills 提供一个单一入口。运行时优先看这里，再按需下钻到具体执行卡或风格卡。

## 1) 选择器层（决定“选什么”）
### 风格卡
- `restrained_bargain`：克制博弈
- `high_density_hook`：高密度卡点爽剧
- `suspense_thriller`：悬疑推进
- `identity_reveal`：身份反转
- `revenge_comeback`：打脸反杀
- `late_rescue`：迟到援军
- `emotion_extreme`：情感极致
- `mistaken_love`：误会虐心
- `office_romance`：职场虐恋
- `comedy_flip`：喜剧反差

### CLIP 类型
- `dialogue`：对话 / 拉扯 / 暧昧 / 对峙
- `action`：打斗 / 追逐 / 推搡 / 摔打 / 快速位移
- `suspense`：线索 / 偷听 / 遮挡 / 反光 / 来电 / 证据推进
- `comedy`：反差 / 误会 / 尴尬 / 梗点 / 节奏包袱
- `reveal`：身份揭露 / 证据公布 / 真相落地

### PROMOTE 模板族
- `T1_NARRATIVE_FLOW`
- `T2_ACTION_TIMELINE`
- `T3_SUSPENSE_EVIDENCE`
- `T4_COMEDY_BEAT`

### 钩子等���
- `LV1`：信息预告
- `LV2`：关系疑云
- `LV3`：身份 / 立场反转
- `LV4`：生死 / 失控 / 强曝光

## 2) 执行层（决定“怎么写”）
### Layer0 v2 执行卡
- 运镜与镜头语言：`kb/layer0/camera-motion-rules.md`
- 描述性优先：`kb/layer0/descriptive-vs-narrative.md`
- 时间戳切片：`kb/layer0/timestamp-blocking.md`
- 三层光影：`kb/layer0/light-structure.md`

## 3) 运行建议
- `generator`：先选风格/CLIP 类型，再用执行卡写分镜
- `packager`：按 CLIP 类型选模板族，渲染时遵守一镜一动与描述性优先
- `qc`：先查裸英文运镜词 / 一镜一动 / 抽象情绪词，再查时间戳与光影是否可执行

## 4) 预算与硬约束
- 10 秒 CLIP 的 rendered 建议：250–450 字
- rendered 硬上限：≤ 550 字
- 时间戳切片：10s / 15s 长度优先使用
- 字数口径：中文字符数（含标点）
