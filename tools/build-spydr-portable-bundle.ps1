param(
    [string]$OutputDir = ""
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
if (-not $OutputDir) {
    $OutputDir = Join-Path $repoRoot "dist\spydr_camicaz_portable_test"
}

$tmpRoot = Join-Path $repoRoot "PC TP IR"
$sourceLib = Join-Path $tmpRoot "TP_Master_version\libcamicaz"
$sourceYCam = Join-Path $tmpRoot "TP_Master_version\yCamicaz"
$sourceYorick = Join-Path $tmpRoot "yorick.git\relocate"
$templateDir = Join-Path $repoRoot "tools\spydr-portable"

if (Test-Path $OutputDir) {
    Remove-Item -LiteralPath $OutputDir -Recurse -Force
}

New-Item -ItemType Directory -Path $OutputDir | Out-Null
New-Item -ItemType Directory -Path (Join-Path $OutputDir "yorick") | Out-Null

Copy-Item -LiteralPath $sourceLib -Destination (Join-Path $OutputDir "libcamicaz") -Recurse
Copy-Item -LiteralPath $sourceYCam -Destination (Join-Path $OutputDir "yCamicaz") -Recurse
Copy-Item -LiteralPath $sourceYorick -Destination (Join-Path $OutputDir "yorick\relocate") -Recurse

Copy-Item -LiteralPath (Join-Path $templateDir "run_spydr_portable.sh") -Destination $OutputDir
Copy-Item -LiteralPath (Join-Path $templateDir "rebuild_portable.sh") -Destination $OutputDir
Copy-Item -LiteralPath (Join-Path $templateDir "README_PORTABLE.md") -Destination $OutputDir

$dirsToRemove = @(
    (Join-Path $OutputDir "libcamicaz\.svn"),
    (Join-Path $OutputDir "libcamicaz\obj"),
    (Join-Path $OutputDir "yCamicaz\.svn"),
    (Join-Path $OutputDir "yCamicaz\obj"),
    (Join-Path $OutputDir "yCamicaz\glade\.svn"),
    (Join-Path $OutputDir "yCamicaz\widgets\.svn"),
    (Join-Path $OutputDir "yCamicaz\yorick\.svn"),
    (Join-Path $OutputDir "yCamicaz\yorick\spydr\.svn")
)

foreach ($dir in $dirsToRemove) {
    if (Test-Path $dir) {
        Remove-Item -LiteralPath $dir -Recurse -Force
    }
}

$filesToRemove = @(
    (Join-Path $OutputDir "libcamicaz\libcamicaz.so"),
    (Join-Path $OutputDir "yCamicaz\yCamicaz.so"),
    (Join-Path $OutputDir "yCamicaz\ywrap.c"),
    (Join-Path $OutputDir "yCamicaz\ywrap.o"),
    (Join-Path $OutputDir "yCamicaz\camicaz.ini~"),
    (Join-Path $OutputDir "yCamicaz\yorick\spydr\spydr.i~"),
    (Join-Path $OutputDir "yCamicaz\yorick\spydr\spydr.py~"),
    (Join-Path $OutputDir "yCamicaz\yorick\spydr\spydr_widgetcam.i~"),
    (Join-Path $OutputDir "yCamicaz\yorick\spydr\#spydr.i#"),
    (Join-Path $OutputDir "yCamicaz\yorick\spydr\#spydr_widgetcam.i#")
)

foreach ($file in $filesToRemove) {
    if (Test-Path $file) {
        Remove-Item -LiteralPath $file -Force
    }
}

Write-Host ""
Write-Host "Portable bundle created:" -ForegroundColor Green
Write-Host "  $OutputDir"
Write-Host ""
Write-Host "Next step on the original Linux machine:"
Write-Host "  1. Copy this whole folder"
Write-Host "  2. Run ./rebuild_portable.sh"
Write-Host "  3. Run ./run_spydr_portable.sh"
