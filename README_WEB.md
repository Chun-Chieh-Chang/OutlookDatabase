# 網頁版 Outlook 郵件資料庫工具

## 新功能

現在您可以使用網頁介面來操作 Outlook 郵件資料庫！

## 安裝與啟動

### 1. 安裝依賴套件
```bash
pip install -r requirements.txt
```

### 2. 建立郵件資料庫（如果還沒有）
```bash
python outlook_db_builder.py
```

### 3. 啟動網頁伺服器
```bash
python web_app.py
```

### 4. 開啟瀏覽器
訪問：http://localhost:5000

## 網頁介面功能

### 📊 **儀表板**
- 總郵件數統計
- 資料庫狀態顯示
- 搜尋結果計數

### 🔍 **郵件搜尋**
- 關鍵字搜尋郵件主旨和內容
- 即時搜尋結果顯示
- 支援中文搜尋

### 👥 **統計分析**
- 主要寄件者排行
- 最近郵件列表
- 郵件來源分析

### 💾 **資料管理**
- 一鍵建立/更新資料庫
- CSV 格式匯出功能
- 資料庫狀態檢查

## 介面特色

- **響應式設計**：支援桌面和行動裝置
- **現代化 UI**：使用 Tailwind CSS 和 Font Awesome 圖示
- **即時更新**：Ajax 非同步載入，無需重新整理頁面
- **載入動畫**：處理過程中的視覺回饋
- **中文介面**：完全中文化的使用者介面

## API 端點

- `GET /` - 主頁面
- `GET /api/stats` - 獲取郵件統計資料
- `POST /api/search` - 搜尋郵件
- `GET /api/export` - 匯出 CSV
- `POST /api/build_database` - 建立資料庫

## 技術架構

- **後端**：Flask 框架
- **前端**：HTML5 + JavaScript + Tailwind CSS
- **資料庫**：SQLite
- **圖示**：Font Awesome

## 使用注意事項

1. 確保 Outlook 桌面應用程式已安裝並配置
2. 首次使用需要先建立資料庫
3. 網頁伺服器預設在 5000 埠運行
4. 大量郵件處理時請耐心等待

## 故障排除

### 無法連接資料庫
- 確認已執行 `outlook_db_builder.py`
- 檢查 `emails.db` 檔案是否存在

### 搜尋無結果
- 確認關鍵字正確
- 檢查資料庫是否包含郵件

### 網頁無法載入
- 確認 Flask 已正確安裝
- 檢查 5000 埠是否被佔用
