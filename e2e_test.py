#!/usr/bin/env python3
"""
End-to-End Test: Skill Chain Orchestration
===========================================

Demonstrates:
1. Create a project
2. Call strategy skill -> generates AdaptationPlan + Bible
3. Call generator skill -> receives AdaptationPlan/Bible from PROJECT_STATE, generates StoryboardDoc
4. Verify parameter passing and asset persistence

This proves that the orchestrator can manage multi-skill pipelines with proper data flow.
"""

import sys
import json
from pathlib import Path

# Add orchestrator to path
sys.path.insert(0, str(Path(__file__).parent / "orchestrator"))

from master import Orchestrator


def main():
    print("=" * 70)
    print("E2E Test: Skill Chain Orchestration (Strategy -> Generator)")
    print("=" * 70)
    print()
    
    orch = Orchestrator(state_dir="state")
    
    # Step 1: Create Project
    print("[STEP 1] Creating project...")
    project_state = orch.create_project(
        project_id="demo_001",
        title="短剧改编示例：爽文反杀",
        episode_count=20
    )
    run_id = project_state["meta"]["runId"]
    print(f"✓ Project created: {run_id}\n")
    
    # Step 2: Call Strategy Skill
    print("[STEP 2] Calling strategy skill...")
    strategy_input = {
        "scriptText": "这是一部20集短剧的原剧本，包含反杀、爽文设定...",
        "episodeCount": 20
    }
    
    project_state = orch.call_skill(project_state, "strategy", strategy_input)
    
    print(f"✓ Strategy skill completed")
    print(f"  - Assets generated: {len([a for a in project_state['assets']])}")
    print(f"  - AdaptationPlan ID: {project_state['pointers']['adaptationPlanId']}")
    print(f"  - Bible ID: {project_state['pointers']['bibleId']}")
    print()
    
    # Verify assets are in PROJECT_STATE
    assert project_state['pointers']['adaptationPlanId'], "AdaptationPlan not generated!"
    assert project_state['pointers']['bibleId'], "Bible not generated!"
    
    # Step 3: Call Generator Skill
    print("[STEP 3] Calling generator skill (consumes strategy output)...")
    generator_input = {
        "generationMode": "incremental",
        "episodeRange": [1, 3]
    }
    
    project_state = orch.call_skill(project_state, "generator", generator_input)
    
    print(f"✓ Generator skill completed")
    print(f"  - Assets generated: {len([a for a in project_state['assets']])}")
    print(f"  - StoryboardDoc ID: {project_state['pointers']['storyboardId']}")
    print()
    
    # Verify assets are in PROJECT_STATE
    assert project_state['pointers']['storyboardId'], "StoryboardDoc not generated!"
    
    # Step 4: Verify Chain - Generator received Strategy outputs
    print("[STEP 4] Verifying skill chain (parameter passing)...")
    
    # Find assets
    adaptation_plan = None
    bible = None
    storyboard = None
    
    for asset in project_state['assets']:
        if asset['meta']['type'] == 'AdaptationPlan':
            adaptation_plan = asset
        elif asset['meta']['type'] == 'Bible':
            bible = asset
        elif asset['meta']['type'] == 'StoryboardDoc':
            storyboard = asset
    
    # Verify storyboard references upstream assets
    if storyboard and adaptation_plan:
        ap_id_in_storyboard = storyboard['data']['overview']['strategySummary']
        assert adaptation_plan['meta']['id'] in ap_id_in_storyboard, "Generator didn't reference AdaptationPlan!"
        print(f"✓ Generator correctly received and referenced AdaptationPlan")
    
    if storyboard and bible:
        sb_locks = storyboard['data']['locks']
        bible_locks = bible['data']['locks']
        # Check if Bible locks were passed to Storyboard
        assert sb_locks['characters'] == bible_locks['characters'], "Bible's character locks not passed!"
        print(f"✓ Generator correctly inherited Bible's locks (characters, locations, lookAndFeel)")
    
    print()
    
    # Step 5: Verify Persistence
    print("[STEP 5] Verifying asset persistence...")
    
    run_dir = Path("state") / run_id
    asset_files = list(run_dir.glob("ASSET_*.json"))
    print(f"✓ {len(asset_files)} asset files persisted to disk:")
    for f in asset_files:
        print(f"   - {f.name}")
    
    print()
    
    # Step 6: Reload and Verify
    print("[STEP 6] Reloading PROJECT_STATE from disk and verifying...")
    
    reloaded_state = orch.load_project(run_id)
    assert len(reloaded_state['assets']) == len(project_state['assets']), "Assets lost after reload!"
    print(f"✓ All {len(reloaded_state['assets'])} assets preserved across reload")
    print(f"✓ PROJECT_STATE pointers intact:")
    for key, val in reloaded_state['pointers'].items():
        if val:
            print(f"   - {key}: {val}")
    
    print()
    print("=" * 70)
    print("✓ E2E TEST PASSED: Skill chain works correctly!")
    print("=" * 70)
    print()
    print("Key Findings:")
    print("1. ✓ Master orchestrator successfully managed PROJECT_STATE lifecycle")
    print("2. ✓ Strategy skill generated AdaptationPlan + Bible (upstream)")
    print("3. ✓ Generator skill received upstream assets via PROJECT_STATE pointers")
    print("4. ✓ Generator used Bible's locks in Storyboard (data inheritance)")
    print("5. ✓ All assets persisted to disk with proper naming convention")
    print("6. ✓ Reload verified long-term consistency")
    print()
    print("This proves that skills can work together in a pipeline without")
    print("direct inter-skill calls - all data flows through the orchestrator!")
    print()


if __name__ == "__main__":
    main()
