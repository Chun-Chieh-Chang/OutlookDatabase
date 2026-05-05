# Skill: SkillsBuilder UI & Search Optimization (Industrial Grade)

## 1. 核心願景 (Vision)
確保 SkillsBuilder AI 介面在任何瀏覽器環境下都能具備「藝術總監級」的視覺表現，並提供「直覺式」的大數據跨年度搜尋體驗。

---

## 2. 快取防禦策略 (Cache-Busting SOP)
### 問題：
瀏覽器常會快取舊的 HTML/CSS，導致修改無效。
### 解決方案：
- **物理更換 (Physical Flip)**：不只是修改 `index.html`，而是直接建立 `index_v3.html` 並在 Flask 路由中切換。
- **內聯樣式 (Inline Priority)**：對核心 UI（如 AI 控制中心）使用 `style="..."`。內聯樣式的權重高於一切，且不會受外部 CSS 檔案快取影響。

---

## 3. 跨年度搜尋導航 (Search UX Pattern)
### 問題：
資料量大時，舊年份資料會被擠到分頁後端，導致用戶誤以為資料遺失。
### 解決方案：
- **年度分佈計算 (Year Dist API)**：搜尋 API 必須回傳各年份的筆數統計。
- **動態導航標籤 (Dynamic Chips)**：前端根據 API 回傳的 `year_distribution` 自動生成跳轉按鈕。
- **一鍵篩選 (Jump Search)**：點擊標籤後自動執行 `keyword + year` 的聯合計算。

---

## 4. 魯棒性防禦 (Robustness Pattern)
### 問題：
UI 變動可能導致 JavaScript 找不到 DOM 元件而崩潰。
### 解決方案：
**必須** 對所有 DOM 操作使用存在性檢查：
```javascript
const el = document.getElementById('target');
if (el) {
    el.classList.add('hidden'); // 安全操作
}
```

---

## 5. 色彩大師規範 (Design Tokens)
- **Primary**: `#3B82F6` (Royal Blue) - 用於主要操作與標題。
- **Surface**: `#FFFFFF` (Pure White) - 用於卡片與面板。
- **Shadow**: `0 30px 60px rgba(15,23,42,0.25)` - 用於營造高端懸浮感。

---

## 6. 維護記錄 (Maintenance)
- **版本**: 1.0.0 (2026-05-05)
- **狀態**: 已部署至 `web_app.py` 路由
- **開發者**: Antigravity (Senior Full-stack Architect & Art Director)
