# 资产规范（Asset Schema）v1.0

## 核心理念
所有技能间的数据传输通过 **JSON 资产** 进行，由 master orchestrator 管理持久化与流转。

## PROJECT_STATE 结构（最小集）

```json
{
  "meta": {
    "runId": "run_20260508_001",
    "projectId": "proj_demo",
    "createdAt": "2026-05-08T10:00:00Z",
    "currentPhase": "N1",
    "status": "running"
  },
  "project": {
    "id": "proj_demo",
    "title": "短剧改编示例",
    "platform": "douyin",
    "aspectRatio": "9:16"
  },
  "pointers": {
    "storySeedId": "",
    "bibleId": "",
    "adaptationPlanId": "",
    "storyboardId": "",
    "promptPackId": "",
    "soundPackId": "",
    "lastQCId": ""
  },
  "settings": {
    "constraintStrength": "S",
    "includeConsistencyDeclaration": true,
    "episodeCount": 20
  },
  "assets": []
}
```

## ASSET 基础结构

每个资产类型都遵循以下最小格式：

```json
{
  "meta": {
    "type": "AdaptationPlan|Bible|StoryboardDoc|SeedancePromptPack|QCReport",
    "id": "ap_xxx|bible_xxx|sb_xxx|pp_xxx|qc_xxx",
    "version": 1,
    "status": "draft|confirmed|failed",
    "createdAt": "2026-05-08T10:00:00Z",
    "updatedAt": "2026-05-08T10:05:00Z",
    "skillName": "strategy|generator|packager|qc",
    "attempt": 1
  },
  "data": {
    // 类型相关字段
  },
  "errors": []
}
```

## 主要资产类型

### 1. AdaptationPlan
- 来源：`script-nucleus-sd2-strategy`
- 包含：改编策略、钩子链、冲突重组

```json
{
  "meta": { "type": "AdaptationPlan", ... },
  "data": {
    "premises": ["设定1", "设定2"],
    "season": {
      "episodeCount": 20,
      "tuiRange": [1, 6],
      "shuangRange": [7, 16],
      "liuRange": [17, 20]
    },
    "strategy": "推-爽-留的多层钩子链"
  }
}
```

### 2. Bible
- 来源：`script-nucleus-sd2-strategy` 初始化，各技能可更新
- 用途：唯一真值源，跨技能共享

```json
{
  "meta": { "type": "Bible", ... },
  "data": {
    "premises": ["设定1"],
    "season": { "episodeCount": 20, ... },
    "locks": {
      "characters": [],
      "locations": [],
      "lookAndFeel": {}
    }
  }
}
```

### 3. StoryboardDoc
- 来源：`script-nucleus-sd2-generator`
- 包含：短剧分镜 Markdown 及结构化数据

```json
{
  "meta": { "type": "StoryboardDoc", ... },
  "data": {
    "format": "CLIP_STANDARD",
    "episodes": [
      {
        "episode": "E1",
        "clips": [
          { "id": "s1e01_c01", "duration": 10, "markdown": "..." }
        ]
      }
    ]
  }
}
```

### 4. SeedancePromptPack
- 来源：`script-nucleus-sd2-packager`
- 包含：可直接投喂 Seedance2 的 prompt

```json
{
  "meta": { "type": "SeedancePromptPack", ... },
  "data": {
    "items": [
      {
        "id": "s1e01_c01",
        "components": { "prefix": "", "locks": {}, "beatMap": [], "bodyNarrative": "", "hook": {} },
        "rendered": "完整 prompt"
      }
    ]
  }
}
```

## 技能调用契约

### 输入（Skill Input Spec）
```json
{
  "skillName": "strategy",
  "version": 1,
  "projectState": { /* PROJECT_STATE */ },
  "input": {
    "scriptText": "原剧本内容",
    "episodeCount": 20
  }
}
```

### 输出（Skill Output Spec）
```json
{
  "status": "success|error|partial",
  "output": {
    "assets": [ { /* 新生成或更新的 ASSET */ } ]
  },
  "errors": [ { "code": "E001", "message": "..." } ],
  "metadata": {
    "executedAt": "2026-05-08T10:05:00Z",
    "durationMs": 1234
  }
}
```

## 规范约束

- **幂等性**：同输入 + 同版本 = 同输出；用 `runId + skillName + attempt` 标识重试
- **字段最小化**：只保留必需字段，避免冗余数据膨胀
- **错误追踪**：所有错误都记录在 `asset.errors[]` 中
- **版本管理**：asset 版本递增，不覆盖旧版本
- **时间戳**：所有重要事件都有 `createdAt/updatedAt`

## 文件持久化

所有资产保存到 `state/` 目录，命名规则：
```
state/
  runs/
    <runId>/
      project_state.json         # 当前项目状态快照
      ASSET_<type>_<id>_v<version>.json
      logs.jsonl                 # 逐行日志
```

## 调用示例（Python）

```python
import json
from pathlib import Path

# 读取当前项目状态
project_state_path = Path("state/project_state.json")
project_state = json.loads(project_state_path.read_text())

# 调用子技能
skill_output = call_skill("strategy", {
    "projectState": project_state,
    "input": { "scriptText": "...", "episodeCount": 20 }
})

# 合并资产
for asset in skill_output["output"]["assets"]:
    project_state["assets"].append(asset)
    # 更新指针
    if asset["meta"]["type"] == "AdaptationPlan":
        project_state["pointers"]["adaptationPlanId"] = asset["meta"]["id"]

# 持久化
project_state_path.write_text(json.dumps(project_state, indent=2, ensure_ascii=False))
```
