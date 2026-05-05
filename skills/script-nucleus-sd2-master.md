---
name: script-nucleus-sd2-master
description: Cherry Studio 总控技能。负责输入路由、资产状态管理、节点化推进与按需调用子SKILL。适用于“任意剧本→红果/抖音短剧→Seedance2生成提示词”全流程，但不强制串行；每次只推进一个节点，保证效率与可控。
---

# script-nucleus-sd2-master（总控）

## 核心目标
1) 节点式推进：评估/策略 → 分镜 →（可选QC）→ SD2 PROMOTE
2) 不强制全流程串行，避免 token 浪费
3) 全程产出可持久化的资产JSON，方便保存/复用/回滚

---

## 运行模式（节点化，不强串行）

### 节点列表
- N0：Intake 路由（短内容/长内容/已短剧化）
- N1：改编策略（阶段0-2）=> AdaptationPlan
- N2：短剧分镜生成（阶段3-6）=> StoryboardDoc
- N3：短剧语法QC（可选）=> QCReport
- N4：Seedance2软约束提示词组装 => SeedancePromptPack
- N5：出片问题诊断/返工建议（可选）=> RepairPlan

### 默认策略（效率优先）
- 已给分镜/CLIP脚本：跳过N1/N2，直接N4
- 只要评估：只做N1
- 要直接出PROMOTE：走 N1 → N2 → N4（N3按需）

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
    "adaptationPlanId": "",
    "storyboardId": "",
    "promptPackId": "",
    "lastQCId": ""
  },
  "settings": {
    "constraintStrength": "S",
    "includeConsistencyDeclaration": true,
    "includeNegative": false
  }
}
```

---

## 两次确认（强制建议）
- 第一次确认：策略（阶段0-2）确认后再生成分镜
- 第二次确认：分镜框架确认后再进入PROMOTE（Seedance2提示词）

---

## 子技能调用约定
- N1：`script-nucleus-sd2-strategy`
- N2：`script-nucleus-sd2-generator`
- N4：`script-nucleus-sd2-packager`
- 按需QC：`script-nucleus-sd2-qc`
