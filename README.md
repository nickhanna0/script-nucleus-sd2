# script-nucleus-sd2

Cherry Studio skills for converting long scripts into short-form vertical drama storyboards and Seedance2-friendly prompts.

## What’s inside

- `skills/`  
  - `script-nucleus-sd2-master.md` — Node-based controller (routing + staged confirmations)
  - `script-nucleus-sd2-strategy.md` — Stage 0–2 adaptation strategy (evaluation + conflict recomposition + multi-scale hook chain)
  - `script-nucleus-sd2-generator.md` — Stage 3–6 storyboard generator + redline QC loop
  - `script-nucleus-sd2-packager.md` — Seedance2 prompt packager (soft constraints S/M/H + consistency declaration)
  - `script-nucleus-sd2-sound-packager.md` — Sound layer last-mile packager (SFX/BGM keywords, adaptive silence)
  - `script-nucleus-sd2-qc.md` — Post-gen QC + minimal-change repair plan

## Key design (learned from live tests)

- **Multi-scale hook chain**: “推/爽/留” must exist at **four** levels simultaneously:
  1) within an episode (0–90s)
  2) within a 3-episode unit (压→释→钩)
  3) within Season S1 segmentation (e.g., 20 eps: 推 1–6 / 爽 7–16 / 留 17–20)
  4) across the full series arc

- **Staged confirmations**:
  - Confirm strategy (Stage 0–2) before generating storyboard.
  - Confirm storyboard framework before composing Seedance2 prompts.

- **Sound is last-mile**:
  - Generate SFX/BGM tags after CLIP content is confirmed (reduce early token use).
  - Prefer adaptive **silence/low-frequency** for threat/forbidden tension.

## Installation (Cherry Studio)

Import all files under `skills/` into your agent.

Recommended entrypoint: `script-nucleus-sd2-master`.
