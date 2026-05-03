# 🔧 AI 整合故障排除指南

## 🚨 已解決的問題

### 1. Unicode 編碼錯誤
**問題**: `UnicodeDecodeError: 'cp950' codec can't decode byte 0xf0`
**原因**: Windows 系統預設使用 CP950 編碼，無法處理 UTF-8 字符
**解決方案**:
```python
# 在 Python 腳本開頭加入
import os
import sys
if sys.platform == "win32":
    os.environ['PYTHONIOENCODING'] = 'utf-8'
```

### 2. AI 模型超時問題
**問題**: `HTTPConnectionPool Read timed out`
**原因**: 
- 模型處理中文文本時間過長
- 提示詞過於複雜
- 模型參數設定不當

**解決方案**:
```python
# 簡化提示詞
prompt = f"Email: {subject} by {sender}"
system_prompt = "Classify this email. Respond with only one: Work, Client, Finance, HR, Tech, Marketing, Personal, or Other."

# 優化模型參數
payload = {
    "model": self.model,
    "prompt": prompt,
    "stream": False,
    "options": {
        "temperature": 0.1,  # 降低隨機性
        "top_p": 0.9,
        "max_tokens": 100   # 限制回應長度
    }
}
```

### 3. 模型回應為空
**問題**: `'NoneType' object has no attribute 'strip'`
**原因**: API 回應格式變更或網路問題
**解決方案**:
```python
result = response.json()
response_text = result.get('response', '')
if response_text:
    return response_text.strip()
else:
    return "模型回應為空"
```

## 🔍 診斷工具

### 檢查 Ollama 服務狀態
```bash
python check_ollama.py
```

### 修復編碼問題
```bash
python fix_encoding.py
```

### 簡化 AI 測試
```bash
python simple_ai_test.py
```

### 單一郵件測試
```bash
python single_email_test.py
```

## ⚡ 效能優化建議

### 1. 模型參數調整
- **temperature**: 0.1-0.3 (降低隨機性)
- **max_tokens**: 50-100 (限制回應長度)
- **timeout**: 60-120秒 (足夠的處理時間)

### 2. 提示詞優化
- 使用簡潔的英文提示
- 避免複雜的格式要求
- 限制輸入文本長度

### 3. 批次處理
- 一次處理多封郵件
- 使用快取機制
- 避免重複分析

## 🛠️ 常見問題解決

### Q: AI 狀態顯示「未設定」
**A**: 
1. 檢查 Ollama 是否運行: `tasklist | findstr ollama`
2. 重新啟動 Ollama 服務
3. 執行 `python fix_encoding.py`

### Q: 分析結果都是「其他」類別
**A**:
1. 檢查提示詞是否過於複雜
2. 使用簡化版本測試
3. 調整模型參數

### Q: 網頁介面無法載入
**A**:
1. 確認 Flask 已安裝: `pip install flask`
2. 檢查 5000 埠是否被佔用
3. 重新啟動 `python web_app.py`

### Q: 記憶體使用過高
**A**:
1. 重啟 Ollama 服務
2. 使用更小的模型
3. 限制同時處理的郵件數量

## 📊 系統監控

### 檢查記憶體使用
```bash
tasklist | findstr ollama
```

### 檢查網路連接
```bash
curl http://localhost:11434/api/tags
```

### 檢查模型狀態
```python
import requests
response = requests.get("http://localhost:11434/api/tags")
print(response.json())
```

## 🔄 重置程序

### 完全重置 AI 服務
1. 終止所有 Ollama 程序
2. 重新啟動 Ollama
3. 測試模型連接
4. 執行 AI 分析測試

### 重新安裝模型
```bash
ollama rm llama3:8b
ollama pull llama3:8b
```

## 📞 技術支援

### 日誌檔案位置
- AI 分析結果: `email_analysis.json`
- 簡化測試結果: `simple_ai_results.json`
- 單一郵件測試: `single_email_analysis.json`
- 系統配置: `ai_config.json`

### 調試模式
```python
# 在 email_analyzer.py 中加入調試輸出
print(f"📝 發送提示: {prompt[:50]}...")
print(f"🤖 模型回應: {result}")
```

## 🎯 最佳實踐

### 1. 定期維護
- 定期重啟 Ollama 服務
- 清理分析快取
- 監控記憶體使用

### 2. 效能監控
- 記錄分析時間
- 監控錯誤率
- 優化批次大小

### 3. 資料備份
- 定期備份分析結果
- 保存重要配置
- 記錄系統變更

## 🚀 未來改進

### 計畫中的優化
- [ ] GPU 加速支援
- [ ] 模型量化
- [ ] 智慧快取機制
- [ ] 自動錯誤恢復
- [ ] 效能監控面板

### 擴展功能
- [ ] 多語言支援
- [ ] 自動分類規則
- [ ] 自定義提示詞
- [ ] 批次匯出功能

---

**如果問題持續存在，請檢查系統日誌並考慮重新安裝 Ollama。**
