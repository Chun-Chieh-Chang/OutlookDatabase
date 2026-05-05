# DEV_LOG.md - SkillsBuilder UI & Search Optimization

## 📅 日誌日期: 2026-05-05

### 1. 失敗嘗試紀錄 (Failed Attempts)
- **嘗試 A**: 直接修改 `index.html` 中的 CSS 與 HTML 結構。
  - **結果**: 瀏覽器快取鎖死，用戶端畫面完全沒改變（按鈕依然是白色框，標題圖示消失）。
- **嘗試 B**: 在 JavaScript 中加入 `alert` 診斷與版本號。
  - **結果**: 雖然邏輯跑通，但 UI 依然混亂，且 Bootstrap 框架與自定義 CSS 發生權重衝突。
- **嘗試 C**: 僅修復 `main.js` 報錯而不處理 HTML 結構缺失。
  - **結果**: 導致 `TypeError: Cannot read properties of null (reading 'classList')`。

### 2. 錯誤原因分析 (Root Cause Analysis)
- **快取機制**: Chrome 瀏覽器對特定 URL 的 HTML 結構有強快取，普通的 `Ctrl + F5` 有時難以徹底清除。
- **檢索截斷**: 資料庫中雖有 8000+ 郵件，但關鍵字「東林易」在 2026 年佔據了前 4 頁，導致用戶以為 2025 年以前的資料不見了。
- **DOM 依賴**: JavaScript 邏輯過度依賴特定 ID（如 `pagination`），在 UI 簡化過程中若漏掉標籤，會導致全局 JS 崩潰。

### 3. 最終矯正措施 (Final Correction)
- **Cache Buster**: 強制將首頁路由切換至物理新檔案 `index_v3.html`。
- **Inline Styles**: 對核心配置面板使用內聯樣式，繞過所有 CSS 快取與權重衝突。
- **Year Navigation**: 在後端加入年份分佈統計，並在前端動態渲染「年度跳轉標籤」。
- **Defensive JS**: 為所有 DOM 操作加上存在性檢查 (`if (el) ...`)，達成工業級穩定性。

### 4. 遺留問題與建議
- 未來若要再次修改 UI，建議直接在 `index_v3.html` 基礎上迭代，並考慮將內聯樣式逐步抽離至具備版本號的 `main.v1.css`。

---
**簽署**: Antigravity (Digital Art Director & Lead Architect)

## 📅 日誌日期: 2026-05-05 (SkillsBuilder 模式啟動)

### 1. 診斷結果 (Diagnosis)
- **UI 違和處**: `index_v3.html` 存在大量內聯樣式，缺乏統一的 Design Tokens；Bootstrap 與自定義樣式衝突。
- **代碼脆弱點**: JavaScript 依賴硬編碼 ID，缺乏防禦性檢查；後端路由混合了過多業務邏輯。
- **MECE 狀態**: `scratch/` 目錄存在冗餘腳本（`fix_all.py`, `ultimate_fixer.py`），需清理。

### 2. 優化計畫 (Strategy)
- **Phase A**: 重新標準化 `index.html`，建立基於 CSS Variables 的設計系統。
- **Phase B**: 重構前端 JavaScript，移除內聯事件監聽，改為模組化監聽。
- **Phase C**: 實施「副作用防禦掃描」，確保 AI 配置更新不會導致同步中斷。

### 3. 即刻執行項
- [x] 將 `index_v3.html` 合併並恢復為 `index.html`。
- [x] 建立 `static/css/index.css` (已整合入 `main.css`)。
- [x] 清理 `scratch/` 冗餘檔案。
- [x] **工業維度重構 (人機料法環測)**：更新 AI 提取邏輯並完成知識遷移。

### 4. 本次改動總結 (Summary of Changes)
- **AI 邏輯升級**: 重新定義 `extract_wiki_entities` 提示詞，引入「人機料法環測」與「5W1H」架構。
- **知識架構重組**: 
    - 建立 `wiki/dimensions/` 分類目錄。
    - 實施 `wiki_migrator.py` 將 274 個實體自動歸類。
    - 生成具備維度層級的 `wiki/index.md`。
- **UI 標準化**: 恢復 `index.html` 為主入口，整合 Design Tokens。

**簽署**: Antigravity (Digital Art Director & Lead Architect)

## 📅 日誌日期: 2026-05-05 (Knowledge Graph v2 Evolution)

### 1. 診斷結果 (Diagnosis) — 7 大結構性缺陷
- **Others 毒桶**: 140/380 頁 (37%) 被歸入 `others/`，LLM 無法有效分類。
- **PDCA/CAPA 全空**: `lifecycle/`, `improvement/` 共 8 個子目錄全部 0 個文件。
- **實體重複**: Mouldex 有 7 個節點、Doris Han 有 4 個節點。
- **類別混淆**: 公司被歸入「Man」，流程被歸入「Material」。
- **缺乏雙向連結**: 無 Obsidian `[[backlink]]` 機制。
- **無 YAML Frontmatter**: 無法進行機器化批量查詢。
- **描述空白 & 編碼腐蝕**: 大量頁面無有效內容。

### 2. 根因分析 (Root Cause)
- **單一根因**: LLM Prompt 不夠好。缺乏 Decision Boundary Rules，LLM 無從判定分類。
- 所有 7 個問題都源自「數據源品質」，下游改造無法修復。

### 3. 矯正措施 (Corrections)
- **email_analyzer.py**: 完全重寫 `extract_wiki_entities()` prompt
  - 新增 11 級 Decision Boundary Rules（按優先順序分類）
  - 新增 PDCA/CAPA 判定規則
  - 新增 `aliases`, `relationships`, `urgency`, `tags`, `domain` 欄位
  - 新增欄位級品質防禦（空值防禦、others→event fallback）
  - 加強 Gemini 429 退避機制（10s base × exponential backoff, 5 retries）
- **wiki_builder.py**: 全面重寫為 v2
  - YAML Frontmatter 寫入（Obsidian-style）
  - Alias Registry（`.alias_registry.json`）實體去重
  - Graph Store（`graph_store.json`）邊持久化
  - `[[wiki-link]]` 雙向連結語法

### 4. 驗證結果 (Validation)
- **測試規模**: 3 封多樣化 email（從 8205 封中取樣）
- **Quality Score**: **100/100** ✅
  - Category ≠ Others: 33/33 (100%)
  - Has Lifecycle: 33/33 (100%)
  - Has Relationships: 33/33 (100%)
- **對比舊 Prompt**: Others 從 37% → 0%、PDCA 從 0% → 100%

### 5. 下一步 (Next Steps)
- [ ] 清空舊 wiki 頁面，用新 prompt 重跑
- [ ] 運行 `wiki_index_gen.py` 重建索引
- [ ] Phase 3: 視覺化 graph_store.json（D3.js 力導向圖）

**簽署**: Antigravity (Digital Art Director & Lead Architect)
