# DEV_LOG: 系統進化與故障確效紀錄 (2026-05-09)

## 1. 故障事件: 編碼回歸與連鎖崩潰 (Major Regression)
* **現象**: 全域 .md 檔案出現問號亂碼，且後端 /api/stats 回傳 500。
* **RCA**: 
    1. PowerShell 讀取 UTF-8 時發生 CP950 誤判。
    2. python -c 傳遞字面量時受終端機編碼污染。
    3. web_app.py 遺失 pandas 導入且存在縮進錯誤。
* **CAPA**: 
    1. 全面廢止透過命令列傳送中文數據，改用 write_to_file 物理寫入。
    2. 在 web_app.py 補齊所有依賴，並通過 python 啟動測試驗證語法。
    3. 實施 safe_read_file 多重回退機制。

## 2. 系統進化: 前端渲染與數據物理清洗
* **變更**: 引入 KaTeX 支援，實施全域 Wiki 物理轉碼 (1443 files) 與檔名重構。
* **確效**: 透過 `browser_subagent` 驗證 KaTeX 解析成功且 "Unknown" 數據徹底消失。

## 3. 重大戰略發現: PDCA 質量起飛定律
* **洞察**: 今日之戰證明，當 PDCA (Plan-Do-Check-Act) 成為全域強制規則，並與「防禦性技能 (Skills)」聯動時，優化質量將發生非線性增長。
* **處置**:
    1. 更新全域開發規則，將 PDCA 設為基準流程。
    2. 建立 `tools/automated_pdca_check.py`，實現「一鍵確效」。
    3. 在 `SYSTEM_GOVERNANCE_PROTOCOL.md` 正式確立「防禦性技能聯動機制」。
* **狀態**: 系統已進入「自癒且防回歸」的工業級成熟期。