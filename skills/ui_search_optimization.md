# Skill: SkillsBuilder UI & Search Optimization (工業級檢索與 UI 優化)

## 1. 核心願景
確保 SkillsBuilder AI 在處理大規模工業數據時，仍能維持極速的響應與直覺的操作體驗，特別是在跨年度數據的定位與 UI 的魯棒性上。

---

## 2. 快取失效與渲染 SOP (Cache-Busting)
### 問題：
開發過程中，瀏覽器常因快取舊版 HTML/CSS 導致新功能失效。
### 解決方案：
- **物理切換 (Physical Flip)**: 不僅修改 `index.html`，必要時建立 `index_v3.html` 並在 Flask 路由中切換。
- **行內優先 (Inline Priority)**: 針對關鍵 UI（如 AI 彈窗），使用行內樣式確保基本結構在 CSS 加載前即正確顯示。

---

## 3. 跨年度檢索模式 (Search UX Pattern)
### 問題：
數據庫跨度過大時，單純關鍵字搜尋會返回過多雜訊。
### 解決方案：
- **年份分佈統計 (Year Dist API)**: API 必須回傳各年份的命中數量。
- **動態過濾標籤 (Dynamic Chips)**: UI 根據 `year_distribution` 自動生成可點擊的年份標籤。
- **一鍵跳轉 (Jump Search)**: 支援 `關鍵字 + 年份` 的複合搜尋邏輯。

---

## 4. DOM 魯棒性守則 (Robustness Pattern)
### 問題：
非同步加載時，JavaScript 常因找不到尚未渲染的 DOM 而崩潰。
### 解決方案：
**強制** 對所有 DOM 操作進行存在性檢查：
```javascript
const el = document.getElementById('target');
if (el) {
    el.classList.add('active'); // 安全執行
}
```

---

## 5. 設計令牌 (Design Tokens)
- **Primary**: `#3B82F6` (皇家藍) - 用於主要操作與標題。
- **Surface**: `#FFFFFF` (純白) - 用於卡片與內容載體。
- **Shadow**: `0 30px 60px rgba(15,23,42,0.15)` - 營造工業級的懸浮感。

---

## 6. 維護紀錄 (Maintenance)
- **版本**: 1.1.0 (2026-05-10)
- **執行人**: Antigravity (Senior Full-stack Architect)
