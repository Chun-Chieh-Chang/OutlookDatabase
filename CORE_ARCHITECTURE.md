# SkillsBuilder 核心架構指南 (Core Architecture Guidelines)
**版本**: 3.2 (Multi-dimensional Industrial Semantic Mapping)

## 1. 願景 (Vision)
建立一個具備「自我進化」能力的工業知識大腦。系統不僅是數據的儲存庫，更是一個動態的推理引擎，能夠自動識別生產過程中的技術維度與因果鏈。

## 2. 四層架構 (Four-Layer Architecture)
1. **數據層 (Ledger)**：從 Outlook 提取的原始 .json 數據，保留所有通訊軌跡。
2. **知識層 (Library/Wiki)**：經過 AI 提煉的結構化維度（HR, PQC, QMS, Spec 等）。
3. **洞察層 (Insights)**：跨維度的關聯性分析與 3D 知識圖譜展示。
4. **演化層 (Evolution)**：透過 PDCA 與 CAPA 紀錄不斷優化的 Prompt 與處理邏輯。

## 3. 硬約束 (Hard Constraints)
* **編碼一致性**: 全專案強制使用 UTF-8 with BOM 以確保 Windows 相容性。
* **副作用防禦**: 任何對 API 或 Model 的修改必須先執行依賴掃描。
* **零拼圖遺漏**: 新增邏輯時必須確保所有引用模組已在頂部導入。

## 4. 故障防禦原則
* **失敗錄入**: 任何 Regression Error 必須錄入 DEV_LOG.md 並執行 CAPA。
* **物理隔離**: 舊版代碼統一存放於 _legacy_archive。