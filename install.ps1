<#
==============================================================================
Antigravity Comic Neubrutalism Theme - 1-Click Installer (Windows PowerShell)
==============================================================================
#>
[CmdletBinding()]
param()

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "================================================================" -ForegroundColor Yellow
Write-Host "  🎨 Antigravity Comic Neubrutalism Theme Installer (Windows)" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Yellow

$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) {
    $Python = Get-Command python3 -ErrorAction SilentlyContinue
}

if ($Python) {
    & $Python.Source "$ScriptDir\install.py"
} else {
    Write-Warning "[!] Python 3 not detected. Attempting native PowerShell installation..."
    $ThemeSource = Join-Path $ScriptDir "theme.css"
    $Css = Get-Content -Raw -Path $ThemeSource
    
    $AppData = [Environment]::GetFolderPath('ApplicationData')
    $TargetDirs = @(
        (Join-Path $AppData "Antigravity\themes"),
        (Join-Path $AppData "Antigravity-Profiles\themes")
    )
    
    foreach ($Dir in $TargetDirs) {
        if (-not (Test-Path $Dir)) {
            New-Item -ItemType Directory -Path $Dir -Force | Out-Null
        }
        $OutPath = Join-Path $Dir "antigravity-comic-theme.css"
        Set-Content -Path $OutPath -Value $Css -Encoding UTF8
        Write-Host "  ✓ Persisted theme to: $OutPath" -ForegroundColor Green
    }
    Write-Host "`n  🎉 Theme installed successfully! Restart Antigravity to apply." -ForegroundColor Green
}
