#!/usr/bin/env python3
"""
Run Full Pipeline: Strategy -> Generator -> Packager -> SoundPackager -> QC

This script demonstrates the full workflow using mock skill wrappers.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "orchestrator"))
from master import Orchestrator


def run_full(script_text: str = "示例原剧本文本", episode_count: int = 20):
    orch = Orchestrator(state_dir="state")
    project_state = orch.create_project(project_id="full_demo", title="Full Pipeline Demo", episode_count=episode_count)
    run_id = project_state["meta"]["runId"]

    # Strategy
    print("-> Running strategy")
    project_state = orch.call_skill(project_state, "strategy", {"scriptText": script_text, "episodeCount": episode_count})

    # Generator
    print("-> Running generator")
    project_state = orch.call_skill(project_state, "generator", {"generationMode": "incremental"})

    # Packager
    print("-> Running packager")
    project_state = orch.call_skill(project_state, "packager", {"strength": "S"})

    # Sound packager
    print("-> Running sound-packager")
    project_state = orch.call_skill(project_state, "sound-packager", {"density": "lite"})

    # QC
    print("-> Running qc")
    project_state = orch.call_skill(project_state, "qc", {})

    print("Full pipeline completed. Assets:")
    for a in project_state.get("assets", []):
        print(f" - {a['meta']['type']}: {a['meta']['id']}")

    print(f"Run directory: state/{run_id}")


if __name__ == "__main__":
    run_full()
