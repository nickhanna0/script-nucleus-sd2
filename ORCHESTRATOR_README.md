# Orchestrator System for script-nucleus-sd2

## 概览

这是一个工程化的技能编排系统，解决了 Cherry Studio 中"子技能无法直接互通"的限制。

**核心设计**：
- **Master Orchestrator** 作为中央控制器，管理 `PROJECT_STATE`
- **JSON 资产**（Asset）作为技能间的数据交互媒介
- **技能包装器**（Wrapper）实现标准化接口，让原有 skill 文档可执行
- **文件持久化**实现长期可复现与审计

## 架构图

```
User / Script Input
        ↓
[Master Orchestrator]
        ↓
    PROJECT_STATE (JSON)
     ↙  ↓  ↘  ↙  ↓  ↘
  Strategy  Generator  Packager
    ↓        ↓         ↓
 [Asset] → [Asset] → [Asset] → ... → Final Output
    ↓        ↓         ↓
  state/runs/<runId>/
    ASSET_AdaptationPlan_*.json
    ASSET_Bible_*.json
    ASSET_StoryboardDoc_*.json
    project_state.json
```

## 关键特性

### 1. 技能间参数传递
- 不依赖"直接函数调用"或"变量共享"
- 所有数据通过 `PROJECT_STATE` 中的 `pointers` 和 `assets` 数组流转
- 每个子技能读取 `PROJECT_STATE`，生成新的 Asset，由 master 合并回去

### 2. 持久化与审计
- 所有资产保存到 `state/runs/<runId>/` 目录
- 每个资产带版本号、时间戳、生成技能信息
- 支持跨会话重放与调试

### 3. 幂等性与错误恢复
- 每次调用带 `runId + skillName + attempt` 标识
- 失败后可修改参数重试
- 不污染已成功的资产

### 4. 易于扩展
- 新增技能只需在 `orchestrator/wrappers/` 下新建脚本
- 遵循标准接口：`skill_main(skill_call) -> skill_output`
- Master 自动发现并调用

## 文件结构

```
.
├── orchestrator/
│   ├── master.py           # 主编排引擎
│   └── wrappers/
│       ├── strategy.py     # Strategy 包装器 (演示)
│       ├── generator.py    # Generator 包装器 (演示)
│       ├── packager.py     # (可选) Packager 包装器
│       └── qc.py           # (可选) QC 包装器
├── state/                  # 运行时状态存储
│   └── runs/
│       └── run_20260508_001_abc123de/
│           ├── project_state.json
│           ├── ASSET_AdaptationPlan_ap_xxx_v1.json
│           ├── ASSET_Bible_bible_xxx_v1.json
│           ├── ASSET_StoryboardDoc_sb_xxx_v1.json
│           └── logs.jsonl
├── docs/
│   ├── ASSET_SCHEMA.md     # 资产规范
│   ├── architecture.md     # 架构文档 (原始)
│   └── ...                 # 原始 skill 文档
├── skills/                 # 原始 skill 文档 (原始)
│   ├── script-nucleus-sd2-master.md
│   ├── script-nucleus-sd2-strategy.md
│   └── ...
├── e2e_test.py             # 端到端测试
└── README.md               # 本文件
```

## 使用方式

### 0. 安装依赖
```bash
# Python 3.8+，无外部依赖
python --version  # Python 3.8+
```

### 1. 创建项目
```bash
python orchestrator/master.py create-project demo "My Short Drama" 20
```

输出会包含 `runId`（如 `run_20260508_001_abc123de`）。

### 2. 调用技能链
```bash
# 获取 runId（从步骤1或通过查看 state/ 目录）
RUN_ID="run_20260508_001_abc123de"

# 调用 strategy 技能
python orchestrator/master.py call-skill "$RUN_ID" strategy '{"scriptText": "原剧本...", "episodeCount": 20}'

# 调用 generator 技能（会自动从 PROJECT_STATE 读取 strategy 的输出）
python orchestrator/master.py call-skill "$RUN_ID" generator '{"generationMode": "incremental"}'

# 调用 packager 技能
python orchestrator/master.py call-skill "$RUN_ID" packager '{"strength": "S"}'
```

### 3. 运行 E2E 测试
```bash
python e2e_test.py
```

输出示例：
```
======================================================================
E2E Test: Skill Chain Orchestration (Strategy -> Generator)
======================================================================

[STEP 1] Creating project...
✓ Project created: run_20260508_001_abc123de

[STEP 2] Calling strategy skill...
✓ Strategy skill completed
  - Assets generated: 2
  - AdaptationPlan ID: ap_20260508100000
  - Bible ID: bible_20260508100000

[STEP 3] Calling generator skill (consumes strategy output)...
✓ Generator skill completed
  - Assets generated: 1
  - StoryboardDoc ID: sb_20260508100001

[STEP 4] Verifying skill chain (parameter passing)...
✓ Generator correctly received and referenced AdaptationPlan
✓ Generator correctly inherited Bible's locks (characters, locations, lookAndFeel)

[STEP 5] Verifying asset persistence...
✓ 3 asset files persisted to disk:
   - ASSET_AdaptationPlan_ap_20260508100000_v1.json
   - ASSET_Bible_bible_20260508100000_v1.json
   - ASSET_StoryboardDoc_sb_20260508100001_v1.json

[STEP 6] Reloading PROJECT_STATE from disk and verifying...
✓ All 3 assets preserved across reload

======================================================================
✓ E2E TEST PASSED: Skill chain works correctly!
======================================================================

Key Findings:
1. ✓ Master orchestrator successfully managed PROJECT_STATE lifecycle
2. ✓ Strategy skill generated AdaptationPlan + Bible (upstream)
3. ✓ Generator skill received upstream assets via PROJECT_STATE pointers
4. ✓ Generator used Bible's locks in Storyboard (data inheritance)
5. ✓ All assets persisted to disk with proper naming convention
6. ✓ Reload verified long-term consistency

This proves that skills can work together in a pipeline without
direct inter-skill calls - all data flows through the orchestrator!
```

## 与 Cherry Studio 的区别

| 特性 | Cherry Studio | Orchestrator System |
|------|---------------|--------------------|
| 子技能互通 | 不支持（需手动复制粘贴） | ✓ 自动通过 PROJECT_STATE |
| 数据持久化 | 仅会话级 | ✓ 文件级（state/ 目录） |
| 可审计性 | 有限（依赖聊天记录） | ✓ 完整的资产历史与版本 |
| 自动化测试 | 困难 | ✓ 支持脚本化与 E2E 测试 |
| 并行执行 | 不支持 | ✓ 支持（需扩展 master） |
| 幂等性 | 无 | ✓ 通过 runId + attempt |
| 易用性 | ✓ 低门槛，即插即用 | 需编程能力，学习曲线 |

## 扩展指南

### 添加新技能包装器

1. 在 `orchestrator/wrappers/` 下创建 `<skill_name>.py`
2. 实现 `skill_main(skill_call: Dict) -> Dict` 函数
3. 遵循输入输出规范（见 ASSET_SCHEMA.md）
4. 从 `skill_call['projectState']['assets']` 读取上游资产

示例（packager）：
```python
def skill_main(skill_call):
    project_state = skill_call['projectState']
    
    # 读取 StoryboardDoc
    storyboard = None
    for asset in project_state['assets']:
        if asset['meta']['type'] == 'StoryboardDoc':
            storyboard = asset
            break
    
    if not storyboard:
        return {"status": "error", "errors": [...]}
    
    # 基于 storyboard 生成 SeedancePromptPack
    prompt_pack = _generate_prompts(storyboard)
    
    return {
        "status": "success",
        "output": {"assets": [prompt_pack]}
    }
```

### 集成 LLM

Master 可以调用任何 LLM API 来处理实际逻辑：

```python
def _generate_adaptation_plan(script_text):
    # 调用 Claude / GPT 等
    response = client.messages.create(
        model="claude-opus",
        messages=[
            {"role": "user", "content": f"改编以下剧本为20集短剧：\n{script_text}"}
        ]
    )
    return parse_adaptation_plan(response.content)
```

## 已知限制与改进方向

- **当前**：同步顺序执行，不支持并行技能
- **改进**：添加任务队列 + 异步执行支持
- **当前**：单机存储（state/ 目录），不支持多人协作
- **改进**：集成 git / 数据库后端实现多人实时协作
- **当前**：技能包装器需手工编写
- **改进**：从原 skill 文档自动生成包装器的代码生成工具

## 验证清单

运行以下检查确保系统正确安装：

- [ ] Python 3.8+ 可用
- [ ] 运行 `python e2e_test.py` 成功
- [ ] `state/` 目录下有新的 `run_*` 目录
- [ ] 新 run 目录内有 3-4 个 ASSET_*.json 文件
- [ ] 所有 asset 的 `meta.type` 与文件名对应

## 常见问题

**Q: 为什么不直接用 Cherry Studio？**  
A: Cherry 很好用但受限于平台。如果你需要长期可复现、多技能协作、自动化测试，Orchestrator 更合适。

**Q: 我能在 Cherry Studio 和 Orchestrator 之间切换吗？**  
A: 可以。Orchestrator 生成的 JSON 资产可导出给 Claude，Claude 也可生成符合资产规范的 JSON。

**Q: 性能如何？**  
A: 演示版本是单线程 + 文件 I/O，足以处理 20-100 集的短剧。大规模生产建议用数据库后端。

## 许可证

与原 script-nucleus-sd2 仓库保持一致。

---

**更新日期**: 2026-05-08  
**作者**: GitHub Copilot  
**仓库**: https://github.com/nickhanna0/script-nucleus-sd2
