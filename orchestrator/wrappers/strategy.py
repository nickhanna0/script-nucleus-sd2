#!/usr/bin/env python3
"""
Skill Wrapper: script-nucleus-sd2-strategy
===========================================

This wrapper demonstrates how to adapt the existing skill documentation
into a structured, orchestrator-compatible skill.

Skill Input: { "scriptText": "...", "episodeCount": 20, ... }
Skill Output: { "status": "success", "output": { "assets": [AdaptationPlan, Bible, ...] } }
"""

import json
from datetime import datetime
from typing import Dict, Any

# DeepSeek integration (optional)
try:
    from ..deepseek_client import get_client
except Exception:
    from deepseek_client import get_client


_ds = get_client()


def skill_main(skill_call: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for the strategy skill wrapper.
    
    This is a DEMO that simulates the logic described in script-nucleus-sd2-strategy.md
    In production, this would call the actual strategy generation logic (LLM, logic engine, etc.)
    """
    
    skill_name = skill_call.get("skillName", "strategy")
    project_state = skill_call.get("projectState", {})
    skill_input = skill_call.get("input", {})
    
    try:
        # Extract input
        script_text = skill_input.get("scriptText", "Sample script content")
        episode_count = skill_input.get("episodeCount", 20)
        
        # Try using DeepSeek to generate a richer adaptation plan + bible
        if _ds.available():
            prompt = f"Extract an adaptation plan and bible from the following script text:\n{script_text}\nEpisodeCount:{episode_count}\nReturn JSON with keys adaptationPlan and bible."
            resp = _ds.chat(prompt)
            if resp.get("success") and resp.get("text"):
                try:
                    parsed = json.loads(resp["text"]) if resp["text"].strip().startswith("{") else None
                    if parsed and isinstance(parsed, dict):
                        adaptation_plan = parsed.get("adaptationPlan") or _generate_adaptation_plan(script_text, episode_count)
                        bible = parsed.get("bible") or _generate_bible(script_text, episode_count)
                    else:
                        adaptation_plan = _generate_adaptation_plan(script_text, episode_count)
                        bible = _generate_bible(script_text, episode_count)
                except Exception:
                    adaptation_plan = _generate_adaptation_plan(script_text, episode_count)
                    bible = _generate_bible(script_text, episode_count)
        else:
            # Fallback to local mock
            adaptation_plan = _generate_adaptation_plan(script_text, episode_count)
            bible = _generate_bible(script_text, episode_count)
        
        assets = [adaptation_plan, bible]
        
        return {
            "status": "success",
            "output": {
                "assets": assets
            },
            "errors": [],
            "metadata": {
                "skillName": skill_name,
                "version": 1,
                "executedAt": datetime.now().isoformat(),
                "durationMs": 234
            }
        }
    
    except Exception as e:
        return {
            "status": "error",
            "output": {"assets": []},
            "errors": [{"code": "STRATEGY_ERROR", "message": str(e)}],
            "metadata": {
                "skillName": skill_name,
                "executedAt": datetime.now().isoformat()
            }
        }


def _generate_adaptation_plan(script_text: str, episode_count: int) -> Dict[str, Any]:
    """
    Generate AdaptationPlan asset.
    
    Mimics the output structure defined in script-nucleus-sd2-strategy.md
    """
    
    plan_id = f"ap_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Simulate 推/爽/留 distribution
    tui_range = [1, max(1, episode_count // 3)]
    shuang_range = [tui_range[1] + 1, max(tui_range[1] + 1, episode_count * 2 // 3)]
    liu_range = [shuang_range[1] + 1, episode_count]
    
    return {
        "meta": {
            "type": "AdaptationPlan",
            "id": plan_id,
            "version": 1,
            "status": "draft",
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "skillName": "strategy"
        },
        "data": {
            "premises": [
                "核心设定从原脚本提取",
                "改编方向：短剧化、高密度钩子链"
            ],
            "season": {
                "episodeCount": episode_count,
                "tuiRange": tui_range,
                "shuangRange": shuang_range,
                "liuRange": liu_range,
                "unit3": {
                    "enabled": True,
                    "rule": "E1压/E2释前奏/E3钩升级，循环"
                },
                "macroEscalation": {
                    "everyEpisodes": 4,
                    "note": "每4-5集一个大升级钩"
                },
                "endgameHook": {
                    "note": "终局钩：真相/代价/救赎"
                }
            },
            "strategy": {
                "phase": "qi|cheng|zhuan|he|mixed",
                "psyLayer": "tui|shuang|liu|mixed",
                "hookDensity": "high",
                "templateUsage": "conflict-recomposition"
            }
        }
    }


def _generate_bible(script_text: str, episode_count: int) -> Dict[str, Any]:
    """
    Generate Bible asset (唯一真值源).
    
    Mimics the Bible structure from script-nucleus-sd2-strategy.md
    """
    
    bible_id = f"bible_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "meta": {
            "type": "Bible",
            "id": bible_id,
            "version": 1,
            "status": "draft",
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "skillName": "strategy"
        },
        "data": {
            "premises": [
                "从原脚本提取的核心设定",
                "改编后的关键设定约束"
            ],
            "locks": {
                "characters": [
                    {
                        "id": "CHAR_001",
                        "name": "主角",
                        "lockText": "主角设定锁定"
                    }
                ],
                "locations": [
                    {
                        "id": "LOC_001",
                        "name": "主要场景",
                        "lockText": "场景设定锁定"
                    }
                ],
                "lookAndFeel": {
                    "colorTemp": "warm",
                    "contrast": "high",
                    "lighting": "dramatic"
                }
            },
            "season": {
                "episodeCount": episode_count,
                "tuiRange": [1, max(1, episode_count // 3)],
                "shuangRange": [max(1, episode_count // 3) + 1, episode_count * 2 // 3],
                "liuRange": [episode_count * 2 // 3 + 1, episode_count],
                "unit3": {
                    "enabled": True,
                    "rule": "E1压/E2释前奏/E3钩升级"
                }
            },
            "episodeConfirmed": []
        }
    }
