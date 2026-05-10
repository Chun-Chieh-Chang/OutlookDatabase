# Skill: Windows Console Encoding Defense (CP950-to-UTF8)
*ID: SKILL-2024-001 | Status: ACTIVE | Occurrence: 3*

## 1. 故障模式 (Failure Mode)
- **類型**: `UnicodeEncodeError`
- **現象**: 執行 Python 腳本時，若輸出包含 Emoji 或特殊中文字元，會導致 `print()` 函數崩潰並終止程式。

## 2. 根因分析 (RCA)
- **直接原因**: Windows 終端機預設編碼 (CP950) 無法映射 UTF-8 專有的多位元組字元。
- **架構原因**: 腳本開發時未考慮到執行環境的編碼限制，缺乏強制的輸出流編碼重定向。

## 3. 預防再發措施 (CAPA) - 核心指令集
在開發任何涉及控制台輸出的 Python 腳本時，必須嚴格遵守：

### A. 強制輸出流重定向
在腳本頂部加入以下防禦程式碼：
```python
import sys
import io

if sys.platform == "win32":
    # 強制將輸出流設為 UTF-8，防止 CP950 崩潰
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

### B. 內容限制
- **禁止使用 Emoji**: 在自動化監測腳本 (PDCA Checkers) 的主要輸出流中禁止使用 Emoji。
- **降級顯示**: 遇到非 ASCII 字元時，優先使用 `errors='replace'` 或 `errors='ignore'`。

## 4. 演化教訓
- 2026-05-10: 由於 `evolve_manual.py` 中的 DNA Emoji 導致手冊更新兩次失敗，正式將此規範提升為系統級強制 Skill。
