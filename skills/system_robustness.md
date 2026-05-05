# Skill: System Robustness & Maintenance (系統魯棒性維護)

## 1. 核心方針
確保系統在面對網路波動、環境差異（Windows/Linux）以及代碼更新時，能保持高度的穩定性與一致性。

## 2. 錯誤防禦規範 (Error Defense)

### A. 雲端 API 韌性 (Cloud API Resilience)
- **原則**：禁止單次請求失敗即中斷。
- **實作**：必須對 `503 Service Unavailable` 與 `429 Too Many Requests` 實作自動重試機制。
- **規範**：重試次數 ≥ 3 次，間隔應隨次數增加（Exponential Backoff）。

### B. 環境編碼相容性 (Encoding Compatibility)
- **原則**：確保在 Windows (CP950) 環境下不因特殊符號崩潰。
- **實作**：在 Python 的 `print` 或 `logging` 中避免使用非標準 Unicode 圖示（如 Emoji），或在程式入口處強制設定 `sys.stdout` 的編碼為 `utf-8`。

## 3. 開發維護 SOP (DevOps SOP)

### A. 後端同步更新 (Backend Sync)
- **動作**：每當修改 `web_app.py`, `email_analyzer.py` 或 `outlook_ingestor.py` 等核心邏輯後，**必須重啟 Flask 伺服器**。
- **目的**：防止伺服器記憶體中殘留舊版邏輯，導致「代碼已改但結果未變」的假性 Bug。

### B. RAG 搜尋品質 (Search Quality)
- 遵循 `rag_chinese_fix.md` 規範，對中文搜尋進行子字串包含檢索，而非完全匹配。

---
*Created by Antigravity - 確保系統永不當機的最後防線*
