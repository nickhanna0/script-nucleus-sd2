#!/usr/bin/env python3
"""
Skill Wrapper: script-nucleus-sd2-idea-cocreation (mock)

Generates a StorySeed asset from a short idea text.
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional

try:
    from ..deepseek_client import get_client
except Exception:
    from deepseek_client import get_client


_ds = get_client()


def skill_main(skill_call: Dict[str, Any]) -> Dict[str, Any]:
    skill_name = skill_call.get("skillName", "idea-cocreation")
    project_state = skill_call.get("projectState", {})
    input_data = skill_call.get("input", {})
    idea_text = input_data.get("ideaText", "一句话: 主角被诬陷")
    
    try:
        if _ds.available():
            prompt = f"Refine the following short idea into a story seed with characters, conflict, and a short beat outline:\n{idea_text}\nReturn JSON with fields originalIdea, refinedConcept, beats."
            resp = _ds.chat(prompt)
            if resp.get("success") and resp.get("text"):
                try:
                    parsed = json.loads(resp["text"]) if resp["text"].strip().startswith("{") else None
                    if parsed and isinstance(parsed, dict):
                        seed = {"meta": {"type": "StorySeed", "id": f"ss_{datetime.now().strftime('%Y%m%d%H%M%S')}", "version": 1, "status": "draft", "createdAt": datetime.now().isoformat(), "skillName": "idea-cocreation-deepseek"}, "data": parsed}
                    else:
                        seed = _generate_story_seed(idea_text)
                except Exception:
                    seed = _generate_story_seed(idea_text)
            else:
                seed = _generate_story_seed(idea_text)
        else:
            seed = _generate_story_seed(idea_text)

        return {"status": "success", "output": {"assets": [seed]}, "errors": [], "metadata": {"skillName": skill_name, "executedAt": datetime.now().isoformat()}}
    except Exception as e:
        return {"status": "error", "output": {"assets": []}, "errors": [{"code": "IDEA_ERROR", "message": str(e)}]}


def _generate_story_seed(idea_text: str) -> Dict[str, Any]:
    ss_id = f"ss_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return {"meta": {"type": "StorySeed", "id": ss_id, "version": 1, "status": "draft", "createdAt": datetime.now().isoformat(), "skillName": "idea-cocreation"}, "data": {"originalIdea": idea_text, "refinedConcept": idea_text + " （已精炼）"}}
