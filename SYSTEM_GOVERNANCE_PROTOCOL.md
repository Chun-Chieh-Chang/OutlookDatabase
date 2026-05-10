# System Governance Protocol: 系統自我進化協議 (Self-Evolution SOP)

## 壹、 核心原則 (Core Principles)
本系統 (SkillsBuilder AI) 之核心價值在於「持續演進」與「故障自癒」。任何代碼變更必須視為對系統穩定性的**挑戰**。

## 貳、 PDCA 工業級確效機制 (Mandatory PDCA/CAPA Loop)
所有開發任務必須嚴格遵守以下體系化流程，不得跳步：

1.  **[Plan] 深度診斷**:
    - 識別「代碼脆弱點」（如：編碼 I/O、併發鎖定）。
    - 預判變更對 UI/UX 藝術一致性的影響。

2.  **[Do] 精準手術**:
    - 執行最小量代碼修改。
    - 同步更新 `DEV_LOG.md`，記錄 **RCA** (根因分析) 與 **CAPA** (矯正預防措施)。

3.  **[Check] 自動化聯動確效 (Skill-Linked Verification)**:
    - **強制執行核心防禦腳本**：在聲明完成前，必須運行 `tools/automated_pdca_check.py`。
    - **Skills 全量調用**：必須逐一核對並執行 `skills/` 目錄下的所有 CAPA 屬性任務：
        - `system_robustness.md`: 檢查 API 韌性與編碼相容性。
        - `rag_chinese_fix.md`: 驗證中文檢索實體匹配。
        - `ui_contrast_standard.md`: 驗證 UI 視覺對比度。
        - `ui_search_optimization.md`: 驗證檢索流程與 DOM 穩定性。
    - **跨模組確效**：如果修改了後端，必須透過 `browser_subagent` 驗證前端渲染。


4.  **[Act] 知識沉澱與推送**:
    - 將本次修正的教訓寫入 `CORE_ARCHITECTURE.md` 或 `SYSTEM_GOVERNANCE_PROTOCOL.md`。
    - 獲得授權後執行 Git Push。

## 參、 自進化與元認知治理 (Self-Evolution & Meta-Cognitive Governance)
為確保 Antigravity 全域進化，系統必須遵守以下高階指令：

1. **元認知錯誤門檻 (Error-to-Skill Trigger)**: 
   - 同類型失效出現次數 **N > 2** 時，必須自動啟動 RCA 並撰寫/更新預防性 Skill。
2. **動態手冊共生 (Dynamic Symbiosis)**: 
   - `MANUAL.md` 必須掛載進化引擎，自動吸納 `skills/` 中的演化教訓。
3. **語義領域優位 (Semantic Supremacy)**: 
   - 廢止 4M1E 等過時硬編碼框架，知識分組必須基於 AI 上下文動態聚類。
4. **環境魯棒性防禦**: 
   - 強制 `utf-8-sig` 編碼與 Windows 環境下的輸出流重定向防禦。
5. **主動式觀測 UI**: 
   - 所有背景異步活動必須具備 UI 脈動反饋，確保開發進度對使用者透明。

## 肆、 失敗預防與回滾 (Regression Prevention)
- **零容忍亂碼**：所有 Markdown 與 Python 檔案強制使用 `utf-8-sig`。
- **依賴最小化**：優先使用 Python 標準庫，避免因外部庫（如 Pandas）缺失導致的環境崩潰。

## 肆、 執行授權與助理約束 (AI Assistant Enforcement)
- **強制讀取**: 本協議為 Antigravity AI 助手的最高行動準則。每次啟動新任務或進行代碼修訂時，助理必須首先確認本協議內容。
- **任務終結標準**: 聲明任務「完成」前，助理必須於回覆末尾列出 PDCA 確效清單，並確認已運行 `automated_pdca_check.py` 且無錯誤。
- **副作用自述**: 若執行過程中發生任何 Regression，助理必須主動揭露並執行 CAPA，嚴禁隱瞞。

---
*Status: Active | Scope: Global Logic | Last Updated: 2026-05-10 (Model Enforcement Hardened)*
