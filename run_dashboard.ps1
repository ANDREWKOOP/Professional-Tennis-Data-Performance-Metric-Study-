param(
    [int]$Port = 8501
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
$Streamlit = Join-Path $ProjectRoot ".venv\Scripts\streamlit.exe"
$App = Join-Path $ProjectRoot "dashboard\streamlit_app.py"

if (!(Test-Path -LiteralPath $Streamlit)) {
    & $Python -m pip install -r (Join-Path $ProjectRoot "requirements-pipeline.txt")
}

& $Streamlit run $App --server.port $Port --server.address 127.0.0.1 --server.headless true --browser.gatherUsageStats false
