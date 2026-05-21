# STW Hub — Build script
# Usage: .\build_apk.ps1
# Auto-detects version from pyproject.toml, builds APK, renames with version tag.

Set-Location $PSScriptRoot

# Read version from pyproject.toml
$version = (Select-String -Path "pyproject.toml" -Pattern 'version\s*=\s*"([^"]+)"' | Select-Object -First 1).Matches.Groups[1].Value
if (-not $version) { Write-Error "Could not read version from pyproject.toml"; exit 1 }

Write-Host "Building STW Hub v$version..." -ForegroundColor Cyan

# Set UTF-8 so flet spinner characters don't crash
chcp 65001 | Out-Null
$env:PYTHONIOENCODING = "utf-8"

# Build
flet build apk
if ($LASTEXITCODE -ne 0) { Write-Error "Build failed"; exit 1 }

# Rename APK
$src  = "build\apk\STWHub.apk"
$dest = "build\apk\STWHub-v$version.apk"
if (Test-Path $dest) { Remove-Item $dest }
Rename-Item $src $dest

Write-Host ""
Write-Host "Done: $dest" -ForegroundColor Green
