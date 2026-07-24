param(
    [int]$StartYear = 2017,
    [int]$EndYear = 2024,
    [int]$Clusters = 7,
    [int]$MinBodyServes = 50,
    [int]$MinBinServes = 10,
    [int]$MinReturnPoints = 1000,
    [switch]$SkipDownload,
    [switch]$SkipInstall
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$VenvPython = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$SystemPython = "C:\Users\max\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

if (!(Test-Path -LiteralPath $VenvPython)) {
    if (!(Test-Path -LiteralPath $SystemPython)) {
        throw "Bundled Python was not found at $SystemPython. Install Python 3.10+ or update run_tennis_project.ps1."
    }
    & $SystemPython -m venv (Join-Path $ProjectRoot ".venv")
}

if (!$SkipInstall) {
    & $VenvPython -m pip install --upgrade pip
    & $VenvPython -m pip install -r (Join-Path $ProjectRoot "requirements-pipeline.txt")
}

$PipelineArgs = @(
    (Join-Path $ProjectRoot "scripts\tennis_capstone_pipeline.py"),
    "--project-root", $ProjectRoot,
    "--start-year", $StartYear,
    "--end-year", $EndYear,
    "--clusters", $Clusters,
    "--min-body-serves", $MinBodyServes,
    "--min-bin-serves", $MinBinServes,
    "--min-return-points", $MinReturnPoints
)

if ($SkipDownload) {
    $PipelineArgs += "--skip-download"
}

& $VenvPython @PipelineArgs

$Rscript = Get-Command Rscript -ErrorAction SilentlyContinue
if ($Rscript) {
    $Report = Join-Path $ProjectRoot "reports\tennis_capstone_report.Rmd"
    & $Rscript.Source -e "rmarkdown::render(normalizePath('$Report', winslash='/'), output_dir=normalizePath('$(Join-Path $ProjectRoot "reports")', winslash='/'))"
} else {
    Write-Host "Rscript was not found, so the RMarkdown file was not rendered. Open reports/tennis_capstone_report.Rmd in RStudio to render it."
}

Write-Host ""
Write-Host "Done. Key outputs:"
Write-Host "  data/processed/"
Write-Host "  reports/portfolio_report.md"
Write-Host "  reports/tennis_capstone_report.Rmd"
