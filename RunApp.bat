@echo off
title Mouldex Knowledge Portal - One Click Start
echo [INFO] 正在啟動 Mouldex 工業知識門戶...

:: 1. 環境偵測與驗證
set "PYTHON_CMD=python"

if exist ".venv\Scripts\python.exe" (
    echo [INFO] 偵測到虛擬環境，正在驗證...
    ".venv\Scripts\python.exe" --version > nul 2>&1
    if not errorlevel 1 (
        echo [INFO] 虛擬環境驗證成功。
        set "PYTHON_CMD=.venv\Scripts\python.exe"
    ) else (
        echo [WARN] 虛擬環境失效，將回退至系統 Python...
    )
)

"%PYTHON_CMD%" --version > nul 2>&1
if errorlevel 1 (
    echo [ERROR] 找不到可用的 Python！請確保已安裝 Python 3.9+ 並加入環境變數。
    pause
    exit /b
)

:: 2. 啟動伺服器
echo [INFO] 正在啟動後台服務 (web_app.py)...
start "" /b "%PYTHON_CMD%" web_app.py

:: 3. 等待服務就緒
echo [INFO] 正在等待服務初始化 (3秒)...
timeout /t 3 /nobreak > nul

:: 4. 自動開啟網頁
echo [INFO] 正在開啟瀏覽器...
start http://localhost:5000

echo.
echo [OK] 服務已啟動！
echo --------------------------------------------------
echo 本地網址: http://localhost:5000
echo --------------------------------------------------
echo [提醒] 請保持此視窗開啟以維持服務執行。
echo.
pause
