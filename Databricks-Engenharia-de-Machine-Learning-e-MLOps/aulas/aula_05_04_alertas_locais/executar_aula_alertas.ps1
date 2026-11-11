param(
    [string]$Inicio = "20260501",
    [string]$Fim = "20260601"
)

$ErrorActionPreference = "Stop"
$Pasta = $PSScriptRoot
$Python = Join-Path $Pasta "monitoramento_e_alertas_local.py"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Arquivo Python da aula nao encontrado."
}

if (Get-Command py -ErrorAction SilentlyContinue) {
    & py -3 -B $Python $Inicio $Fim
}
elseif (Get-Command python -ErrorAction SilentlyContinue) {
    & python -B $Python $Inicio $Fim
}
else {
    throw "Python nao encontrado."
}

if ($LASTEXITCODE -ne 0) {
    throw "Falha na execucao local dos alertas."
}

Write-Host "EXECUCAO LOCAL CONCLUIDA." -ForegroundColor Green