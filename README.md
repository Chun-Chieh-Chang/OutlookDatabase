# SkillsBuilder AI: 工業知識自進化門戶 (Industrial Knowledge Portal)

本系統是一個基於 **PDCA (Plan-Do-Check-Act)** 治理架構的 AI 知識工程平台，旨在將零散的 Outlook 郵件轉化為具備自進化能力的工業知識圖譜。

## 🚀 快速啟動與系統遷移 (Quick Setup & Migration)

如果您想在另一台電腦上運行此系統，請遵循以下步驟：

### 1. 準備環境
- 安裝 **Python 3.10+**。
- 安裝 **Ollama** 並下載模型：`ollama pull gemma2:2b`。

### 2. 安裝依賴庫
```bash
pip install -r requirements.txt
```

### 3. 遷移數據 (選用)
- 將舊電腦的 `emails.db` 與 `wiki/` 目錄直接複製到新電腦的專案根目錄下。

### 4. 啟動服務
```bash
python web_app.py
```
訪問：`http://localhost:5000`

## 🛠️ 核心架構：知識生命週期 (Knowledge Lifecycle)

1. **數據化入 (Ingestion)**: 從 Outlook 提取原始數據並執行原子化 SQL 儲存。
2. **語義聚類 (Semantic Clustering)**: 廢止傳統 4M1E，採用 AI 自動化領域映射與知識歸類。
3. **3D 空間導航 (3D Visualization)**: 提供具備游標連動縮放功能的 3D 知識圖譜。
4. **自進化治理 (Self-Evolution)**: 系統自動從開發與運行錯誤中提煉 CAPA Skill，並動態優化操作手冊。

## 🛠️ 核心功能模組

- **Dashboard**: 實時監控系統進化分數與數據體量。
- **Wiki Explorer**: 多維度檢索與 AI 知識深度合成。
- **System Live Pulse**: 右下角即時推播後端分析軌跡。
- **Evolutionary Manual**: 自動進化的系統操作手冊。

## ⚙️ 開發者操作指南

### 啟動服務端
```bash
python web_app.py
```
訪問：`http://localhost:5000`

### 啟動知識進化引擎 (Batch)
```bash
python wiki_builder.py 1000
```

### 執行治理確效
```bash
python tools/automated_pdca_check.py
```

## 📜 治理協議
本專案嚴格遵守 `SYSTEM_GOVERNANCE_PROTOCOL.md`。所有的變更必須通過 PDCA 循環驗證，並將教訓固化為 `skills/` 下的防禦性腳本。
