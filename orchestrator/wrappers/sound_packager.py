#!/usr/bin/env python3
"""
Skill Wrapper: script-nucleus-sd2-sound-packager (mock)

Generates sound tags (SFX/BGM) for each clip based on storyboard content.
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
    skill_name = skill_call.get("skillName", "sound-packager")
    project_state = skill_call.get("projectState", {})
    
    try:
        storyboard = _find_asset(project_state, "StoryboardDoc")
        if not storyboard:
            return {"status": "error", "output": {"assets": []}, "errors": [{"code": "MISSING_STORYBOARD", "message": "StoryboardDoc not found"}]}
        
        # Try DeepSeek for richer sound tagging
        if _ds.available():
            prompt = f"For the following storyboard, suggest SFX and BGM tags per clip:\n{json.dumps(storyboard, ensure_ascii=False)}\nReturn JSON array items with id, SFX, BGM."
            resp = _ds.chat(prompt)
            if resp.get("success") and resp.get("text"):
                try:
                    parsed = json.loads(resp["text"]) if resp["text"].strip().startswith("[") or resp["text"].strip().startswith("{") else None
                    if isinstance(parsed, list) or (isinstance(parsed, dict) and parsed.get("items")):
                        items = parsed if isinstance(parsed, list) else parsed.get("items")
                        sound_pack = {"meta": {"type": "SoundPack", "id": f"sp_{datetime.now().strftime('%Y%m%d%H%M%S')}", "version": 1, "status": "draft", "createdAt": datetime.now().isoformat(), "skillName": "sound-packager-deepseek"}, "data": {"items": items}}
                    else:
                        sound_pack = _generate_sound_pack(storyboard)
                except Exception:
                    sound_pack = _generate_sound_pack(storyboard)
            else:
                sound_pack = _generate_sound_pack(storyboard)
        else:
            sound_pack = _generate_sound_pack(storyboard)
        return {"status": "success", "output": {"assets": [sound_pack]}, "errors": [], "metadata": {"skillName": skill_name, "executedAt": datetime.now().isoformat()}}
    except Exception as e:
        return {"status": "error", "output": {"assets": []}, "errors": [{"code": "SOUNDPACK_ERROR", "message": str(e)}]}


def _find_asset(project_state: Dict[str, Any], asset_type: str) -> Optional[Dict[str, Any]]:
    for asset in project_state.get("assets", []):
        if asset.get("meta", {}).get("type") == asset_type:
            return asset
    return None


def _generate_sound_pack(storyboard: Dict[str, Any]) -> Dict[str, Any]:
    sp_id = f"sp_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    items = []
    for ep in storyboard.get("data", {}).get("episodes", [])[:3]:
        for clip in ep.get("clips", []):
            sfx = "｜".join(["脚步", "手机震动"]) if "action" in clip.get("type", "") else "｜".join(["呼吸", "低频氛围"])
            bgm = "无声/低频氛围"
            items.append({"id": clip.get("id"), "SFX": sfx, "BGM": bgm})
    
    return {"meta": {"type": "SoundPack", "id": sp_id, "version": 1, "status": "draft", "createdAt": datetime.now().isoformat(), "skillName": "sound-packager"}, "data": {"items": items}}
