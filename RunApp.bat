@echo off
chcp 65001 > nul
title Mouldex Knowledge Portal - One Click Start
echo 🚀 正在啟動 Mouldex 工業知識門戶...

:: 1. 檢測環境並進入虛擬環境
set PYTHON_EXE=python
if exist .venv (
    echo [INFO] 偵測到虛擬環境，正在載入...
    call .venv\Scripts\activate
    :: 驗證虛擬環境內的 Python 是否可用
    python --version > nul 2>&1
    if errorlevel 1 (
        echo [WARN] 虛擬環境配置失效，正在回退至系統 Python...
        set PYTHON_EXE=python
    ) else (
        set PYTHON_EXE=python
    )
) else (
    echo [INFO] 未偵測到虛擬環境，將使用系統 Python。
)

:: 2. 啟動伺服器 (使用 start 確保異步執行)
echo [INFO] 正在啟動後台 Flask 服務 (Entry: web_app.py)...
start /b %PYTHON_EXE% web_app.py

:: 3. 等待服務初始化
echo [INFO] 正在等待服務就緒 (3秒)...
timeout /t 3 /nobreak > nul

:: 4. 自動開啟網頁
echo [INFO] 正在開啟瀏覽器...
start http://localhost:5000

echo.
echo ✅ 服務已啟動！
echo --------------------------------------------------
echo 本地網址: http://localhost:5000
echo --------------------------------------------------
echo [提醒] 請保持此視窗開啟以維持服務執行。
echo.
pause
