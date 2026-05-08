#!/usr/bin/env python3
"""
Skill Wrapper: script-nucleus-sd2-idea-cocreation (mock)

Generates a StorySeed asset from a short idea text.
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional


def skill_main(skill_call: Dict[str, Any]) -> Dict[str, Any]:
    skill_name = skill_call.get("skillName", "idea-cocreation")
    project_state = skill_call.get("projectState", {})
    input_data = skill_call.get("input", {})
    idea_text = input_data.get("ideaText", "一句话: 主角被诬陷")
    
    try:
        seed = _generate_story_seed(idea_text)
        return {"status": "success", "output": {"assets": [seed]}, "errors": [], "metadata": {"skillName": skill_name, "executedAt": datetime.now().isoformat()}}
    except Exception as e:
        return {"status": "error", "output": {"assets": []}, "errors": [{"code": "IDEA_ERROR", "message": str(e)}]}


def _generate_story_seed(idea_text: str) -> Dict[str, Any]:
    ss_id = f"ss_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return {"meta": {"type": "StorySeed", "id": ss_id, "version": 1, "status": "draft", "createdAt": datetime.now().isoformat(), "skillName": "idea-cocreation"}, "data": {"originalIdea": idea_text, "refinedConcept": idea_text + " （已精炼）"}}
