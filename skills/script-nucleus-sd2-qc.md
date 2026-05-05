---
name: script-nucleus-sd2-qc
description: Seedance2友好QC与返工建议。输入StoryboardDoc或PromptPack以及用户对生成视频的反馈，输出漂移风险、可生成性问题、以及最小改动返工建议（不要求全流程重跑）。
---

# script-nucleus-sd2-qc

## 输入
- StoryboardDoc / SeedancePromptPack
- 用户反馈（失败类型）：如“角色变脸”“镜头没快切”“动作太僵硬”“场景漂移”“出现文字水印”
- 可选：用户提供生成视频截图/描述

## 输出
- QCReport（问题分类 + 严重级别）
- RepairPlan（最小改动策略：改前缀/改声明/改某CLIP几句/升档位S→M等）

## 最小改动优先级（从低到高）
1) 仅增强一致性声明（不改正文）
2) S→M（加强人物/场景锚点短句）
3) 对单个CLIP的镜1-4做局部改写（不动其他CLIP）
4) 返回generator阶段4/5局部返工
