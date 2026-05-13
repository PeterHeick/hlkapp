#Requires -Version 5.1
<#
.SYNOPSIS
    Bygger KlinikPortal Windows-installer.
.DESCRIPTION
    1. Bygger Vue-frontend
    2. Kopierer dist/ til backend/src/klinik/static/dist/
    3. Kører PyInstaller
    4. Kører Inno Setup → installer/KlinikPortal-0.1.0-setup.exe
.NOTES
    Kræver: Python 3.13 + uv, Node.js + npm, Inno Setup 6 (ISCC.exe i PATH eller standardsti)
#>
[CmdletBinding()]
param()

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = $PSScriptRoot

function Step([string]$msg) {
    Write-Host "`n==> $msg" -ForegroundColor Cyan
}

# --- 1. Frontend-build ---
Step "Bygger Vue-frontend"
Push-Location "$root\frontend"
try {
    npm ci --prefer-offline
    npm run build
} finally {
    Pop-Location
}

# --- 2. Kopiér dist til static ---
Step "Kopierer frontend/dist -> backend/src/klinik/static/dist"
$src  = "$root\frontend\dist"
$dest = "$root\backend\src\klinik\static\dist"
if (Test-Path $dest) { Remove-Item $dest -Recurse -Force }
Copy-Item $src $dest -Recurse

# --- 3. Tilføj PyInstaller hvis mangler ---
Step "Sikrer PyInstaller >= 6.6 er tilstede"
uv add --optional packaging "pyinstaller>=6.6"

# --- 4. PyInstaller ---
Step "Kører PyInstaller"
Push-Location $root
try {
    uv run pyinstaller KlinikPortal.spec --clean --noconfirm
} finally {
    Pop-Location
}

# --- 5. Inno Setup ---
Step "Kører Inno Setup"
$iscc = $null
$candidates = @(
    "ISCC.exe",
    "$env:ProgramFiles\Inno Setup 6\ISCC.exe",
    "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
)
foreach ($c in $candidates) {
    if (Get-Command $c -ErrorAction SilentlyContinue) { $iscc = $c; break }
    if (Test-Path $c) { $iscc = $c; break }
}
if (-not $iscc) {
    Write-Error "ISCC.exe ikke fundet. Installer Inno Setup 6 fra https://jrsoftware.org/isdl.php"
}

New-Item -ItemType Directory -Force -Path "$root\installer" | Out-Null
& $iscc "$root\KlinikPortal.iss"

Step "Faerdig! Installer: installer\KlinikPortal-0.1.0-setup.exe"
