#!/usr/bin/env python3
"""
Master Orchestrator for script-nucleus-sd2 Skill System
=========================================================

Responsibilities:
- PROJECT_STATE management and persistence
- Skill lifecycle (trigger, input/output validation, asset merging)
- Error handling and repair suggestions
- Audit logging
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid


class Orchestrator:
    def __init__(self, state_dir: str = "state"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(exist_ok=True)
        
    def create_project(self, project_id: str, title: str, episode_count: int = 20) -> Dict[str, Any]:
        """Create a new project with initial PROJECT_STATE."""
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        project_state = {
            "meta": {
                "runId": run_id,
                "projectId": project_id,
                "createdAt": datetime.now().isoformat(),
                "currentPhase": "N0",
                "status": "initialized"
            },
            "project": {
                "id": project_id,
                "title": title,
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
                "includeConsistencyDeclaration": True,
                "episodeCount": episode_count
            },
            "assets": [],
            "changelog": []
        }
        
        # Create run directory
        run_dir = self.state_dir / run_id
        run_dir.mkdir(exist_ok=True)
        
        # Persist
        state_file = run_dir / "project_state.json"
        self._save_json(state_file, project_state)
        
        print(f"[INFO] Project created: {run_id}")
        return project_state
    
    def load_project(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Load PROJECT_STATE from disk."""
        state_file = self.state_dir / run_id / "project_state.json"
        if not state_file.exists():
            print(f"[ERROR] Project not found: {run_id}")
            return None
        return self._load_json(state_file)
    
    def call_skill(self, project_state: Dict[str, Any], skill_name: str, skill_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a skill wrapper and merge returned assets into PROJECT_STATE.
        
        Args:
            project_state: Current PROJECT_STATE
            skill_name: e.g., "strategy", "generator", "packager"
            skill_input: Input parameters for the skill
        
        Returns:
            Updated PROJECT_STATE with new assets
        """
        run_id = project_state["meta"]["runId"]
        run_dir = self.state_dir / run_id
        
        # Prepare skill invocation
        skill_call = {
            "skillName": skill_name,
            "version": 1,
            "projectState": project_state,
            "input": skill_input
        }
        
        # Call skill (via wrapper)
        print(f"[INFO] Calling skill: {skill_name}")
        skill_output = self._invoke_skill_wrapper(skill_name, skill_call)
        
        if skill_output["status"] == "error":
            print(f"[ERROR] Skill failed: {skill_output['errors']}")
            return project_state
        
        # Merge assets
        for asset in skill_output.get("output", {}).get("assets", []):
            project_state["assets"].append(asset)
            
            # Update pointer
            asset_type = asset["meta"]["type"]
            pointer_map = {
                "AdaptationPlan": "adaptationPlanId",
                "Bible": "bibleId",
                "StoryboardDoc": "storyboardId",
                "SeedancePromptPack": "promptPackId",
                "SoundPack": "soundPackId",
                "QCReport": "lastQCId"
            }
            if asset_type in pointer_map:
                project_state["pointers"][pointer_map[asset_type]] = asset["meta"]["id"]
        
        # Update phase and persist
        project_state["meta"]["currentPhase"] = self._next_phase(project_state["meta"]["currentPhase"])
        project_state["meta"]["updatedAt"] = datetime.now().isoformat()
        
        state_file = run_dir / "project_state.json"
        self._save_json(state_file, project_state)
        
        # Log asset persistence
        for asset in skill_output.get("output", {}).get("assets", []):
            asset_file = run_dir / f"ASSET_{asset['meta']['type']}_{asset['meta']['id']}_v{asset['meta']['version']}.json"
            self._save_json(asset_file, asset)
        
        print(f"[INFO] Skill completed: {skill_name}, {len(skill_output.get('output', {}).get('assets', []))} assets generated")
        return project_state
    
    def _invoke_skill_wrapper(self, skill_name: str, skill_call: Dict[str, Any]) -> Dict[str, Any]:
        """
        Load and execute a skill wrapper.
        
        Wrappers are Python modules in orchestrator/wrappers/ that implement
        the skill interface: skill_main(skill_call) -> skill_output
        """
        # Allow skill names with '-' or '_' by normalizing to file names
        normalized_name = skill_name.replace('-', '_')
        wrapper_file = Path(__file__).parent / "wrappers" / f"{normalized_name}.py"
        
        if not wrapper_file.exists():
            return {
                "status": "error",
                "errors": [{"code": "WRAPPER_NOT_FOUND", "message": f"Wrapper not found: {skill_name}"}]
            }
        
        # Dynamically import and execute
        import importlib.util
        # Use normalized module name when importing
        spec = importlib.util.spec_from_file_location(normalized_name, wrapper_file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        try:
            return module.skill_main(skill_call)
        except Exception as e:
            return {
                "status": "error",
                "errors": [{"code": "EXECUTION_ERROR", "message": str(e)}]
            }
    
    @staticmethod
    def _save_json(path: Path, data: Dict[str, Any]) -> None:
        """Save JSON with pretty printing."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    
    @staticmethod
    def _load_json(path: Path) -> Dict[str, Any]:
        """Load JSON from file."""
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            # Fallback for Windows encoding issues
            return json.loads(path.read_text(encoding="gbk"))
    
    @staticmethod
    def _next_phase(current_phase: str) -> str:
        """Progress to next phase in the workflow."""
        phases = ["N0", "N1", "N2", "N3", "N4", "N5"]
        if current_phase in phases:
            idx = phases.index(current_phase)
            return phases[idx + 1] if idx + 1 < len(phases) else current_phase
        return current_phase


def main():
    """CLI for orchestrator."""
    if len(sys.argv) < 2:
        print("Usage: master.py <command> [args]")
        print("  create-project <project_id> <title> [episode_count]")
        print("  load-project <run_id>")
        print("  call-skill <run_id> <skill_name> <input_json>")
        sys.exit(1)
    
    orch = Orchestrator()
    command = sys.argv[1]
    
    if command == "create-project":
        project_id = sys.argv[2] if len(sys.argv) > 2 else "demo"
        title = sys.argv[3] if len(sys.argv) > 3 else "Demo Project"
        episode_count = int(sys.argv[4]) if len(sys.argv) > 4 else 20
        project_state = orch.create_project(project_id, title, episode_count)
        print(json.dumps(project_state, indent=2, ensure_ascii=False))
    
    elif command == "load-project":
        run_id = sys.argv[2]
        project_state = orch.load_project(run_id)
        if project_state:
            print(json.dumps(project_state, indent=2, ensure_ascii=False))
    
    elif command == "call-skill":
        run_id = sys.argv[2]
        skill_name = sys.argv[3]
        skill_input = json.loads(sys.argv[4]) if len(sys.argv) > 4 else {}
        
        project_state = orch.load_project(run_id)
        if project_state:
            updated_state = orch.call_skill(project_state, skill_name, skill_input)
            print(json.dumps(updated_state, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
