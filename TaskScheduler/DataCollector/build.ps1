# PowerShell Build Script for DataCollector Windows Executable
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SrcDir = Join-Path $ScriptDir "src"
$DistDir = Join-Path $ScriptDir "dist"
$BuildWork = Join-Path $ScriptDir ".build_work"

Write-Host "`n=====================================================================" -ForegroundColor Cyan
Write-Host " AI TASK SCHEDULER: DATA COLLECTOR — POWERSHELL BUILD" -ForegroundColor Cyan
Write-Host "=====================================================================`n" -ForegroundColor Cyan

Write-Host "--> [1/3] Installing/verifying build dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install pyinstaller customtkinter pystray pillow darkdetect

Write-Host "`n--> [2/3] Running automated unit test suite..." -ForegroundColor Yellow
python -m unittest discover -s (Join-Path $ScriptDir "tests") -p "test_*.py" -v
if ($LASTEXITCODE -ne 0) {
    Write-Error "Unit tests failed. Aborting build."
    exit $LASTEXITCODE
}

Write-Host "`n--> [3/3] Compiling DataCollector.exe with PyInstaller..." -ForegroundColor Yellow
pyinstaller `
    --noconfirm `
    --onefile `
    --windowed `
    --name DataCollector `
    --distpath $DistDir `
    --workpath $BuildWork `
    --specpath $ScriptDir `
    --paths $SrcDir `
    --add-data "$SrcDir/schema.json;." `
    --add-data "$SrcDir/db_schema.sql;." `
    (Join-Path $SrcDir "main.py")

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n=====================================================================" -ForegroundColor Green
    Write-Host " BUILD SUCCESSFUL!" -ForegroundColor Green
    Write-Host " Standalone Windows Executable: $DistDir\DataCollector.exe" -ForegroundColor Green
    Write-Host "=====================================================================`n" -ForegroundColor Green
} else {
    Write-Error "PyInstaller build failed."
    exit $LASTEXITCODE
}
