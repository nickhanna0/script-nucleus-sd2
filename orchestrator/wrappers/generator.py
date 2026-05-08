#!/usr/bin/env python3
"""
Skill Wrapper: script-nucleus-sd2-generator
============================================

Demonstrates how to receive output from upstream skill (strategy) and generate next asset.

Input: AdaptationPlan + Bible from PROJECT_STATE pointers
Output: StoryboardDoc
"""

import json
from datetime import datetime
from typing import Dict, Any, Optional


def skill_main(skill_call: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for the generator skill wrapper.
    
    Receives PROJECT_STATE which contains pointers to AdaptationPlan and Bible
    Generates StoryboardDoc based on those inputs
    """
    
    skill_name = skill_call.get("skillName", "generator")
    project_state = skill_call.get("projectState", {})
    skill_input = skill_call.get("input", {})
    
    try:
        # Retrieve upstream assets from PROJECT_STATE
        adaptation_plan = _find_asset(project_state, "AdaptationPlan")
        bible = _find_asset(project_state, "Bible")
        
        if not adaptation_plan or not bible:
            return {
                "status": "error",
                "output": {"assets": []},
                "errors": [{"code": "MISSING_UPSTREAM", "message": "AdaptationPlan or Bible not found"}]
            }
        
        # Generate storyboard
        storyboard = _generate_storyboard(adaptation_plan, bible, project_state)
        
        return {
            "status": "success",
            "output": {
                "assets": [storyboard]
            },
            "errors": [],
            "metadata": {
                "skillName": skill_name,
                "version": 1,
                "executedAt": datetime.now().isoformat(),
                "durationMs": 567,
                "upstreamAssets": {
                    "adaptationPlanId": adaptation_plan["meta"]["id"],
                    "bibleId": bible["meta"]["id"]
                }
            }
        }
    
    except Exception as e:
        return {
            "status": "error",
            "output": {"assets": []},
            "errors": [{"code": "GENERATOR_ERROR", "message": str(e)}]
        }


def _find_asset(project_state: Dict[str, Any], asset_type: str) -> Optional[Dict[str, Any]]:
    """
    Find an asset by type in PROJECT_STATE.assets array.
    """
    for asset in project_state.get("assets", []):
        if asset.get("meta", {}).get("type") == asset_type:
            return asset
    return None


def _generate_storyboard(
    adaptation_plan: Dict[str, Any],
    bible: Dict[str, Any],
    project_state: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate StoryboardDoc based on AdaptationPlan and Bible.
    
    This is a DEMO that generates a simple storyboard structure.
    In production, this would use LLM + Layer0 rules to generate full storyboards.
    """
    
    sb_id = f"sb_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    episode_count = project_state.get("settings", {}).get("episodeCount", 20)
    
    # Generate a simple storyboard with placeholder clips
    episodes = []
    for ep_num in range(1, min(episode_count + 1, 4)):  # Demo: first 3 episodes
        clips = []
        for clip_num in range(1, 4):  # 3 clips per episode
            clip_id = f"s1e{ep_num:02d}_c{clip_num:02d}"
            clips.append({
                "id": clip_id,
                "duration": 10,
                "type": "dialogue" if clip_num % 2 == 0 else "action",
                "markdown": f"# {clip_id}\n\n省略号表示镜头描述：\n第{clip_num}镜：人物对话/动作，推动情节...\n\n钩子：LV{clip_num}"
            })
        
        episodes.append({
            "episode": f"E{ep_num}",
            "clips": clips
        })
    
    return {
        "meta": {
            "type": "StoryboardDoc",
            "id": sb_id,
            "version": 1,
            "status": "draft",
            "createdAt": datetime.now().isoformat(),
            "updatedAt": datetime.now().isoformat(),
            "skillName": "generator"
        },
        "data": {
            "format": "CLIP_STANDARD",
            "overview": {
                "episodeCount": episode_count,
                "totalDurationSec": episode_count * 30 * 10,  # Rough estimate
                "strategySummary": f"基于 AdaptationPlan {adaptation_plan['meta']['id']} 生成"
            },
            "locks": {
                "globalPrefix": "",
                "characters": bible.get("data", {}).get("locks", {}).get("characters", []),
                "locations": bible.get("data", {}).get("locks", {}).get("locations", []),
                "lookAndFeel": bible.get("data", {}).get("locks", {}).get("lookAndFeel", {})
            },
            "episodes": episodes
        }
    }
