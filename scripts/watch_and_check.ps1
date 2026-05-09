# SkillsBuilder Code Watcher
# Watches for file changes and triggers Sanity Check automatically

$path = Get-Location
$filter = '*.*'

$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = $path
$watcher.Filter = $filter
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

$action = {
    $path = $Event.SourceEventArgs.FullPath
    $changeType = $Event.SourceEventArgs.ChangeType
    
    # Only check core files
    if ($path -match "index.html|main.js|web_app.py") {
        Write-Host ""
        Write-Host "------------------------------------------------" -ForegroundColor Cyan
        Write-Host "检测到文件变更: $path ($changeType)" -ForegroundColor Yellow
        Write-Host "正在执行自动化卫生检查..." -ForegroundColor Gray
        
        # Run the Python sanity check
        python scripts/sanity_check.py
        
        Write-Host "------------------------------------------------" -ForegroundColor Cyan
    }
}

Register-ObjectEvent $watcher "Changed" -Action $action
Register-ObjectEvent $watcher "Created" -Action $action

Write-Host "🚀 SkillsBuilder 守護進程已啟動！" -ForegroundColor Green
Write-Host "正在監控 $path 中的代碼變更..."
Write-Host "只要儲存檔案，系統就會自動進行衛生檢查。 (按下 Ctrl+C 停止)"

while ($true) { Start-Sleep -Seconds 1 }
