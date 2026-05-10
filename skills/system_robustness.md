# Skill: System Robustness & Maintenance (系統魯棒性與維護)

## 1. 核心願景
建立具備「自我修復」能力的工業知識大腦。系統應在面對 API 不穩定、編碼回歸或硬體限制時，仍能維持高度的一致性與可靠性。

## 2. 故障防禦原則 (Error Defense)

### A. 雲端 API 韌性 (Cloud API Resilience)
- **場景**: 頻繁調用 Gemini API 導致速率限制或逾時。
- **策略**: 實施指數退避 (Exponential Backoff) 機制。
- **規範**: 預設重試 3 次，間隔隨次數增加。

### B. 編碼相容性 (Encoding Compatibility)
- **場景**: 在 Windows (CP950) 環境下處理 UTF-8 知識庫導致亂碼。
- **策略**: 全專案強制使用 `utf-8-sig` (BOM) 並使用 `safe_read_file` 函數進行多重回退讀取。
- **規範**: 嚴禁在命令列直接傳遞非 ASCII 字串。
- **演化教訓**: 
    - 寫入 JSON 或 Markdown 時必須指定 `encoding='utf-8-sig'`，否則不同工具間會出現解碼衝突。
    - 在 Python List Comprehension 中並行打開同一個檔案進行讀寫會導致檔案截斷 (Truncation) 為 0 或是僅剩 BOM，必須分步處理。
- **數據恢復演化**: 
    - 原始數據目錄 (`raw/emails/`) 可能會因為腳本錯誤而清空，必須確保 `emails.db` 作為終極真理 (Source of Truth) 的完整性。
    - 應定期檢查檔案大小，若出現大規模 0-byte 檔案，應自動觸發從 DB 恢復的機制。

## 3. 持續整合 SOP (DevOps SOP)

### A. 後端熱同步 (Backend Sync)
- **規則**: 修改 `web_app.py` 或 API 邏輯後，必須手動重啟 Flask 服務。
- **驗證**: 確保 `/api/ai_status` 恢復為綠色 (Available)。

### B. RAG 品質確效 (Search Quality)
- 參考 `rag_chinese_fix.md` 進行實體匹配測試，確保「工業關鍵字」與「Wiki 檔案名」完美對齊。

---
*Created by Antigravity - 專為工業知識圖譜設計的防禦性技能*
