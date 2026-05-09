# SkillsBuilder AI 系統操作手冊

## 1. 系統進化流程
1. **數據化入 (Sync)**：原始郵件提取。
2. **維度對應 (Mapping)**：語意標籤歸類。
3. **深度合成 (Synthesis)**：Local LLM 知識提煉。

## 2. 進化程度量化定義 (Evolution Metrics)

$$Evolution Score = (R_{syn} \times 0.4) + (D_{link} \times 15) + \log_{10}(V_{email} + 1) \times 2$$

## 3. 故障防禦與 CAPA 守則
* **RCA**: 深度分析 ANSI/CP950 與 UTF-8 的編碼衝突。
* **CAPA**: 建立 `safe_read_file` 自動探針機制，防止回歸錯誤。