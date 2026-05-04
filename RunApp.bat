@echo off
echo ===================================================
echo   SkillsBuilder Pro: Outlook Database Tool
echo ===================================================
echo.
echo [1/2] Checking dependencies...
pip install -r requirements.txt --quiet

echo [2/2] Starting Web Server...
echo.
echo Application will be available at: http://localhost:5000
echo.
start http://localhost:5000
python web_app.py
pause
