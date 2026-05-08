#!/usr/bin/env python3
"""
Skill Wrapper: script-nucleus-sd2-qc (mock)

Performs QC checks on StoryboardDoc and PromptPack, returns QCReport and optional RepairPlan.
"""
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

try:
    from ..deepseek_client import get_client
except Exception:
    from deepseek_client import get_client


_ds = get_client()


def skill_main(skill_call: Dict[str, Any]) -> Dict[str, Any]:
    skill_name = skill_call.get("skillName", "qc")
    project_state = skill_call.get("projectState", {})
    
    try:
        storyboard = _find_asset(project_state, "StoryboardDoc")
        prompt_pack = _find_asset(project_state, "SeedancePromptPack")
        if not storyboard:
            return {"status": "error", "output": {"assets": []}, "errors": [{"code": "MISSING_STORYBOARD", "message": "StoryboardDoc not found"}]}
        
        # Optionally ask DeepSeek to review and suggest repairs
        findings, repair_plan = _run_qc_checks(storyboard, prompt_pack)
        if _ds.available():
            prompt = f"Perform QC on the storyboard and prompt pack. Return JSON with findings (list) and repairPlan (list).\nStoryboard:{json.dumps(storyboard, ensure_ascii=False)}\nPromptPack:{json.dumps(prompt_pack, ensure_ascii=False)}"
            resp = _ds.chat(prompt)
            if resp.get("success") and resp.get("text"):
                try:
                    parsed = json.loads(resp["text"]) if resp["text"].strip().startswith("{") else None
                    if parsed and isinstance(parsed, dict):
                        findings = parsed.get("findings", findings)
                        repair_plan = parsed.get("repairPlan", repair_plan)
                except Exception:
                    pass

        qc_report = _make_qc_report(findings, repair_plan)
        
        return {"status": "success", "output": {"assets": [qc_report]}, "errors": [], "metadata": {"skillName": skill_name, "executedAt": datetime.now().isoformat()}}
    except Exception as e:
        return {"status": "error", "output": {"assets": []}, "errors": [{"code": "QC_ERROR", "message": str(e)}]}


def _find_asset(project_state: Dict[str, Any], asset_type: str) -> Optional[Dict[str, Any]]:
    for asset in project_state.get("assets", []):
        if asset.get("meta", {}).get("type") == asset_type:
            return asset
    return None


def _run_qc_checks(storyboard: Dict[str, Any], prompt_pack: Optional[Dict[str, Any]]):
    findings: List[Dict[str, Any]] = []
    repair_steps: List[str] = []
    # Simple mock checks
    episodes = storyboard.get("data", {}).get("episodes", [])
    if not episodes:
        findings.append({"severity": "high", "message": "No episodes generated"})
        repair_steps.append("Regenerate Storyboard with generator")
    else:
        # check clip lengths
        for ep in episodes:
            for clip in ep.get("clips", []):
                if clip.get("duration", 0) <= 0:
                    findings.append({"severity": "medium", "message": f"Clip {clip.get('id')} has non-positive duration"})
                    repair_steps.append(f"Set duration for {clip.get('id')} to 10s")
    
    # prompt pack checks
    if prompt_pack:
        items = prompt_pack.get("data", {}).get("items", [])
        if not items:
            findings.append({"severity": "medium", "message": "Prompt pack has no items"})
            repair_steps.append("Run packager with different settings")
    else:
        findings.append({"severity": "low", "message": "No prompt pack to check"})
        repair_steps.append("Create prompt pack via packager")

    return findings, repair_steps


def _make_qc_report(findings, repair_plan):
    qc_id = f"qc_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    return {"meta": {"type": "QCReport", "id": qc_id, "version": 1, "status": "draft", "createdAt": datetime.now().isoformat(), "skillName": "qc"}, "data": {"findings": findings, "repairPlan": repair_plan}}
