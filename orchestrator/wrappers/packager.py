#!/usr/bin/env python3
"""
Skill Wrapper: script-nucleus-sd2-packager (mock)

Generates a SeedancePromptPack asset from a StoryboardDoc.
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional


def skill_main(skill_call: Dict[str, Any]) -> Dict[str, Any]:
    skill_name = skill_call.get("skillName", "packager")
    project_state = skill_call.get("projectState", {})
    
    try:
        # Find StoryboardDoc
        storyboard = _find_asset(project_state, "StoryboardDoc")
        if not storyboard:
            return {"status": "error", "output": {"assets": []}, "errors": [{"code": "MISSING_STORYBOARD", "message": "StoryboardDoc not found"}]}
        
        # Create prompt pack (mock rendered prompt)
        prompt_pack = _generate_prompt_pack(storyboard, project_state)
        
        return {"status": "success", "output": {"assets": [prompt_pack]}, "errors": [], "metadata": {"skillName": skill_name, "executedAt": datetime.now().isoformat()}}
    except Exception as e:
        return {"status": "error", "output": {"assets": []}, "errors": [{"code": "PACKAGER_ERROR", "message": str(e)}]}


def _find_asset(project_state: Dict[str, Any], asset_type: str) -> Optional[Dict[str, Any]]:
    for asset in project_state.get("assets", []):
        if asset.get("meta", {}).get("type") == asset_type:
            return asset
    return None


def _generate_prompt_pack(storyboard: Dict[str, Any], project_state: Dict[str, Any]) -> Dict[str, Any]:
    pp_id = f"pp_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    items = []
    for ep in storyboard.get("data", {}).get("episodes", [])[:3]:
        for clip in ep.get("clips", []):
            item = {
                "id": clip.get("id"),
                "components": {"prefix": [], "locks": {}, "beatMap": [], "bodyNarrative": clip.get("markdown", ""), "hook": {}},
                "rendered": f"PROMPT for {clip.get('id')}: {clip.get('markdown')[:80]}"
            }
            items.append(item)
    
    return {
        "meta": {"type": "SeedancePromptPack", "id": pp_id, "version": 1, "status": "draft", "createdAt": datetime.now().isoformat(), "skillName": "packager"},
        "data": {"items": items}
    }
