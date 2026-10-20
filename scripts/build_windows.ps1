$ErrorActionPreference = "Stop"

if ($env:OS -ne "Windows_NT") {
  throw "This build script must run on Windows. PyInstaller does not cross-compile for Windows."
}

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
  throw "Install the Python launcher for Windows, then rerun this script."
}

py -3.14 -m venv .venv-build
if ($LASTEXITCODE -ne 0) { throw "Could not create the build environment." }

$python = Join-Path (Get-Location) ".venv-build\Scripts\python.exe"
& $python -m pip install --upgrade pip
& $python -m pip install -r requirements.txt -r requirements-dev.txt
if ($LASTEXITCODE -ne 0) { throw "Could not install pinned project dependencies." }

$browserDir = Join-Path (Get-Location) "vendor\ms-playwright"
New-Item -ItemType Directory -Force -Path $browserDir | Out-Null
$env:PLAYWRIGHT_BROWSERS_PATH = $browserDir
& $python -m playwright install chromium
if ($LASTEXITCODE -ne 0) { throw "Could not install the pinned Playwright Chromium." }

& $python -m PyInstaller --noconfirm --clean --onedir --name PublicAdInspector `
  --collect-all playwright `
  --collect-all pydantic `
  --add-data "app\static;app\static" `
  --add-data "app\detection\terms.json;app\detection" `
  --add-data "schemas\result.schema.json;schemas" `
  launcher.py
if ($LASTEXITCODE -ne 0) { throw "PyInstaller build failed." }

$distBrowserDir = Join-Path (Get-Location) "dist\PublicAdInspector\ms-playwright"
New-Item -ItemType Directory -Force -Path $distBrowserDir | Out-Null
Copy-Item -Path (Join-Path $browserDir "*") -Destination $distBrowserDir -Recurse -Force
Write-Host "Build output: $(Join-Path (Get-Location) 'dist\PublicAdInspector')"
