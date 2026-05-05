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

## [2026-05-04] SkillsBuilder Phase 2: Refactoring & Standardization
### Diagnosis
- **RCA**:
    - `index.html` remains monolithic (1400+ lines) with mixed styling standards.
    - Workflow indicators are static and don't reflect real-time backend state.
    - Lack of mobile-first navigation controls (no hamburger menu).
    - JS logic scattered throughout HTML template.
- **CAPA**:
    - Extract JS into `static/js/main.js`.
    - Standardize all UI components to use CSS Variables (Design Tokens).
    - Implement dynamic state-driven workflow logic.
    - Add mobile navigation toggle and responsive refinement.

### Tasks
- [x] Initialize `static/js/main.js` and extract logic.
- [x] Refactor `index.html` for component consistency.
- [x] Standardize color system to CSS variables.
- [x] Implement Mobile Menu Toggle.
- [x] Verify all API connections and error handling (Robustness Check).
- [x] Implement "One-Click Execution" pipeline (Ingest + Wiki Build).

## [2026-05-04] Emergency Fix: JS SyntaxError & Robustness Refinement
### Diagnosis
- **RCA**: 
    - `index.html` had duplicate `<script>` tags for `main.js`, leading to "Identifier 'currentSearchType' has already been declared" error.
    - Multiple UI functions called in `index.html` were missing from `main.js`.
    - Backend referred to missing modules (`outlook_builder_menu.py`).
- **副作用防禦 (Side-effect Defense)**:
    - Ensured `main.js` functions handle missing DOM elements gracefully.
    - Modified `outlook_ingestor.py` to be callable with parameters without breaking its standalone usage.

### CAPA
- **index.html**: Removed redundant script inclusion.
- **main.js**: 
    - Implemented missing UI and AI tool functions.
    - Added interactivity for plan selection.
    - Improved event handling in `showView`.
- **web_app.py**:
    - Localized `PLANS` configuration.
    - Replaced broken imports with `outlook_ingestor`.
- **outlook_ingestor.py**: 
    - Refactored `ingest_emails` to accept `max_emails` and `body_limit`.

### Tasks
- [x] Fix duplicate script inclusion (SyntaxError resolved).
- [x] Implement missing frontend logic in `main.js`.
- [x] Restore backend extraction functionality by redirecting to `outlook_ingestor.py`.
- [x] Update documentation and Dev Log.

## [2026-05-04] SkillsBuilder Phase 2: Refinement & Standardization
### Diagnosis
- **RCA**:
    - CSS variable inconsistency (`--space-X` vs `--spacing-X`) causing layout failures.
    - Style fragmentation between `index.html` and `main.css`.
    - UI components (Stats Strip, Search Bar) lacked SkillsBuilder premium feel.
- **CAPA**:
    - Consolidated all styles into `main.css`.
    - Corrected all spacing variables to `--space-X`.
    - Redesigned Hero section with `hero-glow` and `hero-subtitle`.
    - Refined Search UI and Tool Cards for premium industrial aesthetics.
    - Implemented SSE Streaming for real-time pipeline progress feedback.
    - Resolved browser 'Tracking Prevention' warnings by implementing local hosting for assets.

### Tasks
- [x] Consolidate styles into `main.css`.
- [x] Fix CSS variable naming (`--space-X`).
- [x] Redesign `Hero Section` and `Stats Strip`.
- [x] Refine `Search Bar` with smooth transitions.
- [x] Implement SSE Streaming for real-time pipeline progress feedback.
- [x] Fully eliminate CDN warnings via local hosting.

### ✨ UI/UX Phase A Completed
- [x] Implemented 'Data Capsules' for hero stats.
- [x] Standardized professional iconography (replaced Emojis with FA Icons).
- [x] Enhanced card elevation and hover interactions.
- [x] Refined typography and color hierarchy.

### ✨ UI/UX Phase B Completed
- [x] Implemented 'Liquid Shimmer' effect for CTA buttons.
- [x] Added 'Breathing Glow' animation for Search Focus.
- [x] Upgraded Loading Spinner to Dual-Ring Gradient system.
- [x] Enhanced micro-animations for dashboard state indicators.

### 📊 UI/UX Dashboard Initialized
- [x] Implemented 'Knowledge Insights' dashboard for empty-state landing.
- [x] Added backend API for aggregate wiki and email statistics.
- [x] Created 'Smart Suggestions' cards to guide user interaction.
- [x] Optimized workspace transition logic (Dashboard -> Results).

## [2026-05-05] Search Visibility & Data Integrity Enhancement
### Diagnosis
- **RCA**: 
    - Search limit in `web_app.py` was hardcoded to `LIMIT 20`.
    - Due to the high volume of recent emails (2026), the top 20 results were always occupied by the most recent year, effectively hiding data from 2025, 2024, etc.
    - Lack of result count UI made it unclear to the user if they were seeing a complete set of results.
- **副作用防禦 (Side-effect Defense)**:
    - Increased limit to 500 to balance visibility and performance.
    - Added UI feedback (count) to prevent confusion when results are capped.

### CAPA
- **web_app.py**: Increased SQL `LIMIT` from 20 to 500.
- **index.html**: Added `searchCount` placeholder in the results header.
- **main.js**: Implemented logic to update `searchCount` text content upon search completion.

### Tasks
- [x] Identify root cause of hidden historical data (Hardcoded Limit).
- [x] Increase backend search limit (20 -> 500).
- [x] Implement frontend result count display.
- [x] Verify data distribution across years (2022-2026 verified in DB).

## [2026-05-05] Search Pagination & UX Optimization
### Diagnosis
- **RCA**: 
    - Previous fix expanded search limit to 500, but a long list of results is difficult to navigate.
    - Large result sets can impact frontend rendering performance if handled as a single block.
- **副作用防禦 (Side-effect Defense)**:
    - Implemented server-side pagination to ensure fast response times regardless of total result count.
    - Maintained state (`searchState`) in frontend to prevent keyword/page desynchronization.

### CAPA
- **web_app.py**: 
    - Enhanced `/api/search` to support `page` and `limit` parameters.
    - Integrated `OFFSET` logic in SQL query.
    - Added total page calculation and total result count in response.
- **index.html**: Added pagination control bar with "Previous", "Next", and "Page Info" status.
- **main.js**: 
    - Implemented `searchState` global object.
    - Added `changePage` function and refined `searchEmails` for paginated fetching.
    - Added smooth scroll-to-top behavior when switching pages.

### Tasks
- [x] Implement server-side pagination logic (SQL OFFSET/LIMIT).
- [x] Build responsive pagination UI controls.
- [x] Implement frontend state management for search pagination.
- [x] Add visual feedback for disabled pagination states.

## [2026-05-05] AI Query Robustness & Config Fix
### Diagnosis
- **RCA**: 
    - AI Query returned "API 錯誤: 404".
    - Investigation revealed `ai_config.json` was set to `llama3.2:3b`, but the local Ollama instance only had `llama3.2:latest`.
    - Ollama returns 404 (Not Found) when the requested model tag does not exist.
    - Previous `check_ollama_connection` only verified if the service was alive, not if the specific model was available.
- **副作用防禦 (Side-effect Defense)**:
    - Enhanced `EmailAnalyzer` to verify model existence during connection check.
    - Corrected `ai_config.json` to use the available `latest` tag.

### CAPA
- **ai_config.json**: Updated `model` from `llama3.2:3b` to `llama3.2:latest`.
- **email_analyzer.py**: Upgraded `check_ollama_connection` to scan the local model list and verify the presence of the configured model.
- **Backend Trigger**: Executed manual API reconnect to reload the fixed configuration without requiring a full server restart.

### Tasks
- [x] Identify root cause of "404" (Missing model tag in Ollama).
- [x] Update `ai_config.json` to match available local models.
- [x] Enhance `EmailAnalyzer` connection check for better error reporting.
- [x] Verify fix with manual API test (Status 200 confirmed).

## [2026-05-05] AI Brain Evolution: Gemini 1.5 Flash Integration
### Diagnosis
- **RCA**: 
    - Local Llama 3.2 3B is insufficient for complex cross-email reasoning and RAG.
    - User has hardware constraints preventing the use of larger local models (e.g., 70B).
- **副作用防禦 (Side-effect Defense)**:
    - Maintained full backward compatibility with Ollama for users preferring local-only processing.
    - Added API key validation to prevent application crashes on invalid config.

### CAPA
- **ai_config.json**: 
    - Introduced `provider` selector (`ollama` vs `google`).
    - Added `google` configuration section for API Key and model selection.
- **email_analyzer.py**: 
    - Refactored core AI calling logic into a multi-provider dispatcher.
    - Implemented `call_gemini` using Google's Generative AI REST API.
    - Upgraded `check_ollama_connection` to act as a universal connectivity validator.

### Tasks
- [x] Refactor `EmailAnalyzer` for provider-agnostic architecture.
- [x] Implement Google Gemini 1.5 Flash REST integration.
- [x] Update configuration schema for cloud providers.
- [x] Verify provider switching logic.

## [2026-05-05] UI/UX: AI Core Settings Management
### Diagnosis
- **RCA**: 
    - Manually editing `ai_config.json` is prone to errors and unintuitive for non-developers.
    - Switching between local and cloud providers required a server restart or manual API call.
- **副作用防禦 (Side-effect Defense)**:
    - Implemented API key masking (showing only start/end characters) in the UI to prevent accidental exposure during demonstrations.
    - Added a validation layer to ensure the server re-initializes correctly after a config change.

### CAPA
- **web_app.py**: 
    - Added `/api/ai_config` for secure configuration retrieval.
    - Added `/api/ai_config_update` for real-time model/provider switching.
- **index.html**: 
    - Implemented a high-fidelity Settings Modal with conditional field rendering based on the selected provider.
    - Added a gear icon in the global status bar for quick access.
- **main.js**: 
    - Developed the logic for dynamic configuration loading, password toggling, and persistence.

### Tasks
- [x] Build Backend configuration management API.
- [x] Design and implement the Settings Modal UI.
- [x] Integrate frontend state with backend persistence.
- [x] Add API Key security masking.



## [2026-05-05] UI/UX: Transition to Non-Blocking Inline Loading
### Diagnosis
- **RCA**: 
    - AI query used a full-screen `loadingOverlay` which blocked the entire UI.
    - This created a disruptive experience for quick analytical tasks.
- **副作用防禦 (Side-effect Defense)**:
    - Retained full-screen overlay only for mission-critical/heavy operations (Full Sync, Ingest).
    - Implemented a separate inline loading system for fast data-retrieval tasks.

### CAPA
- **index.html**: 
    - Inserted `#inlineLoading` container directly below the search bar.
    - Designed it with backdrop-blur and a subtle pulse animation for a premium feel.
- **main.js**: 
    - Decoupled `showLoading` (modal) and `showInlineLoading` (non-modal).
    - Updated `searchEmails` and `askWiki` to utilize the new inline system.
    - Added logic to temporarily hide results during loading to reduce visual noise.

### Tasks
- [x] Design and implement `#inlineLoading` UI component.
- [x] Refactor `main.js` to support multi-tier loading states.
- [x] Transition Search/AI flows to non-blocking interaction model.
- [x] Verify layout stability during loading state transitions.




