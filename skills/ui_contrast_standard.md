# UI 對比度與視覺層次規範 (SkillsBuilder AI Standard)

> [!IMPORTANT]
> 此規範旨在確保 SkillsBuilder AI 在任何環境（淺色/深色模式）下均具備專業級的資訊辨識度與美感。

## 1. 字體與對比度 (Typography Contrast)

### 淺色模式 (Light Mode)
- **背景底色**: `#F9FAFB` 或 `#FFFFFF`
- **主標題 (H1-H3)**: 必須使用 `#111827` (曜石黑) 以強化視認度，字重建議 `800`。
- **正文段落 (P/LI)**: 必須使用 `#4B5563` (灰度 600) 以維持閱讀舒適度，字重不低於 `400`。
- **強調文字 (Strong)**: 使用 `#3B82F6` (品牌藍) 增加視覺錨點。

### 深色模式 (Dark Mode)
- **背景底色**: `#0F172A` (深藍黑)
- **主標題 (H1-H3)**: 必須使用 `#F1F5F9` (雲母白)，字重建議 `800`。
- **正文段落 (P/LI)**: 必須使用 `#94A3B8` (灰度 400)，字重不低於 `450`。
- **強調文字 (Strong)**: 使用 `#60A5FA` (天藍) 提升視覺層次。

## 2. 主題隔離實踐 (Theme Isolation)

嚴禁使用硬編碼 (Hardcoded) 的 `background: white` 或 `color: black`。必須使用 CSS 變數或動態切換：

```css
/* 淺色模式區塊 */
:root:not([data-theme="dark"]) .card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
}

/* 深色模式區塊 */
[data-theme="dark"] .card {
    background: #1E293B;
    border: 1px solid #334155;
}
```

## 3. 數據回饋彈性 (Data Resilience)

當後端傳回缺失數據時，UI 必須以優雅的方式進行替換，嚴禁直接顯示 `Unknown` 或 `0`。

- **Unknown Sender** -> `系統匿名寄件者`
- **Unknown Time** -> `日期不詳`
- **佈局**: Margin/Padding 符合 4px 倍數，卡片具備細微懸浮感。
- **演化教訓**: 
    - UI 狀態必須與後端數據編碼同步。
    - 在編碼修復期間，前端 404 應被視為數據重建的正常中間狀態，而非系統性故障。
調用 `EmailAnalyzer.get_entity_context()` 進行即時補完。

## 4. 驗證清單 (Validation Checklist)
- [ ] 在 375px 行動裝置寬度下，正文與背景的對比度是否符合 WCAG AA 標準？
- [ ] 切換模式時，所有 `.prose` 容器是否同步更新？
- [ ] 是否存在任何行內 (Inline) 的 `style` 屬性？（必須移除）

---
*Created by Antigravity - 專為工業知識圖譜設計的視覺守則*
