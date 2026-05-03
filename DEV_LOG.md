# Development Log - Outlook Database Tool

## Project Overview
- **Goal**: Professional-grade Outlook email database management with AI insights.
- **Architect**: Antigravity (SkillsBuilder Mode)
- **Design Standard**: SkillsBuilder Color Master Palette

## [2026-05-03] Initial SkillsBuilder Activation
### Diagnosis
- **RCA (Root Cause Analysis)**:
    - Large monolithic `index.html` (82KB) causing maintenance difficulty.
    - Duplicate `<main>` tags in `index.html`.
    - Lack of formal Wiki for knowledge persistence.
    - Synchronous AI/DB operations in Flask.
- **CAPA (Corrective and Preventive Actions)**:
    - Initialize Wiki structure.
    - Split CSS into separate files.
    - Refactor HTML structure.
    - Implement Design Tokens.

### Tasks
- [x] Initialize `DEV_LOG.md`
- [x] Initialize `wiki/` structure
- [x] Refactor `index.html` (CSS extraction & tag fix)
- [x] Implement SkillsBuilder Design Tokens (Day/Night support)
- [x] Implement Full Content Ingestor (including attachments)
- [x] Implement Karpathy Ingest Workflow (Raw -> Wiki Entities)
- [x] Integrate Wiki UI into the Dashboard

## [2026-05-03] Knowledge-Evolving Architecture Complete
### RCA
- Original system was "lossy" and lacked contextual knowledge.
- No direct link between emails and high-level project concepts.

### CAPA
- **outlook_ingestor.py**: Captures full body and extracts attachments to `raw/attachments/`.
- **wiki_builder.py**: Upgraded to **DeepSeek-V3 (671B-Cloud)** for superior architectural reasoning and entity extraction.
- **Web UI**: Added "Wiki" navigation and "Full Ingest" action for a seamless Karpathy-style workflow.
- **Dependency Fix**: Resolved `pywin32` installation and `cp950` encoding issues on Windows.

## [2026-05-03] AI Brain Upgrade
### Diagnosis
- **RCA**: `llama3.2:3b` lacks the reasoning depth required for complex project entity mapping and concept abstraction.
### CAPA
- Successfully switched to `deepseek-v3.1:671b-cloud` via Ollama Cloud Bridge.
- Verified structural JSON extraction with the new model.
- Performance significantly improved in context understanding.
