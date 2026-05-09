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
    - **跨模組確效**：如果修改了後端，必須透過 `browser_subagent` 驗證前端渲染。

4.  **[Act] 知識沉澱與推送**:
    - 將本次修正的教訓寫入 `CORE_ARCHITECTURE.md` 或 `SYSTEM_GOVERNANCE_PROTOCOL.md`。
    - 獲得授權後執行 Git Push。

## 參、 失敗預防與回滾 (Regression Prevention)
- **零容忍亂碼**：所有 Markdown 與 Python 檔案強制使用 `utf-8-sig`。
- **依賴最小化**：優先使用 Python 標準庫，避免因外部庫（如 Pandas）缺失導致的環境崩潰。

---
*Status: Active | Scope: Global Logic | Last Updated: 2026-05-09 (Re-hardened)*
