@echo off
title SkillsBuilder AI Portable
setlocal enabledelayedexpansion

echo [SkillsBuilder] 正在檢查 Python 環境...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] 找不到 Python。請先安裝 Python 並加入 PATH。
    pause
    exit /b
)

echo [SkillsBuilder] 啟動智慧核心...
python bootstrap.py
pause
