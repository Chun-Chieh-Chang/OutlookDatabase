# SkillsBuilder AI 系統操作手冊
*最後進化時間：2026-05-10*

## 0. 系統功能與操作說明
本系統旨在將零散的 Outlook 郵件轉化為結構化的工業知識庫。

### A. 數據分析儀表板 (Dashboard)
- **實時監控**：顯示郵件總量、技術實體數及系統進化分數。
- **動態看板**：右下角「System Live Pulse」即時推播後端分析進度。

### B. 3D 知識圖譜 (3D Knowledge Graph)
- **視覺導航**：左鍵旋轉、右鍵平移。
- **精準縮放**：滾輪縮放基準點已與游標連動，指向哪裡即縮放哪裡。
- **一鍵還原**：右上角「還原全貌」按鈕可平滑重置視野。

### C. 技術百科 (Wiki Repository)
- **語義領域聚類 (Semantic Domain Clustering)**：知識不再按傳統維度劃分，而是根據郵件上下文自動生成的「語義領域」進行聚類。
- **AI 深度合成**：在實體頁面點擊「立即合成」，系統將從萬封郵件中提煉技術因果關係。

### D. 生產管道 (Knowledge Pipeline)
- **自動化同步**：一鍵啟動從 Outlook 抓取、SQL 儲存到 Wiki 生成的全流程。

## 1. 系統進化流程 (Knowledge Lifecycle)
1. **數據化入 (Ingestion)**：原始郵件提取與原子化儲存。
2. **語義映射 (Semantic Mapping)**：利用 LLM 進行自動化標籤歸類與實體鏈接。
3. **知識合成 (Synthesis)**：將碎片化訊息轉化為高保真技術文檔。

## 2. 進化程度量化定義 (Evolution Metrics)
> [!NOTE]
> 系統進化分數反映了知識庫的健康度與智慧化程度。

$$ EvolutionScore = (R_{syn} 	imes 0.4) + (D_{link} 	imes 15) + \log_{10}(V_{email} + 1) 	imes 2 $$

| 參數 | 定義 | 說明 |
| :--- | :--- | :--- |
| **$R_{syn}$** | 合成率 | 已完成 AI 深度合成的實體比例 |
| **$D_{link}$** | 連結密度 | 實體間的平均關聯強度與密度 |
| **$V_{email}$** | 數據體量 | 系統閱歷的廣度與樣本基數 |

## 3. 故障防禦與 CAPA 守則 (系統自動演化紀錄)
以下內容由系統根據 PDCA 週期自動從執行經驗中提煉：

- **來自 rag_chinese_fix.md**: - 寫入 JSON 或 Markdown 時必須指定 `encoding='utf-8-sig'`，否則不同工具間會出現解碼衝突。
    - 原始數據恢復應優先從 `emails.db` 進行原子重建，而非依賴不穩定的檔案緩存。
    - **技術 ID 歸併 (v1.3)**: 料號（如 R1-1000 vs R1-10000）可能存在誤打 (Typo)，系統應對編輯距離 < 2 的技術代碼進行模糊預警或別名合併。
- **來自 system_robustness.md**: - 寫入 JSON 或 Markdown 時必須指定 `encoding='utf-8-sig'`，否則不同工具間會出現解碼衝突。
    - 在 Python List Comprehension 中並行打開同一個檔案進行讀寫會導致檔案截斷 (Truncation) 為 0 或是僅剩 BOM，必須分步處理。
- **來自 ui_contrast_standard.md**: - UI 狀態必須與後端數據編碼同步。
    - 在編碼修復期間，前端 404 應被視為數據重建的正常中間狀態，而非系統性故障。
調用 `EmailAnalyzer.get_entity_context()` 進行即時補完。

## 4. 系統確效標準
- **編碼完整性**：全專案強制 utf-8-sig。
- **數據完整性**：拒絕 0-byte 檔案。
- **UI 相容性**：支援 375px 行動裝置優先。
