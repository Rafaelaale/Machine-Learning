$ErrorActionPreference = "Stop"

$Projeto = Split-Path $PSScriptRoot -Parent
$Repo = Join-Path $Projeto "docker-automation"
$App = Join-Path $Repo "burguer-app"

Set-Location $Projeto

$Falhas = 0
$Avisos = 0

function VerificarArquivo {
    param(
        [string]$Descricao,
        [string]$Caminho
    )

    if (Test-Path $Caminho -PathType Leaf) {
        Write-Host "OK: $Descricao" -ForegroundColor Green
    }
    else {
        Write-Host "AUSENTE: $Descricao" -ForegroundColor Yellow
        $script:Falhas++
    }
}

Write-Host "`n===== ESTRUTURA DOS MICROSSERVICOS =====" -ForegroundColor Cyan

foreach ($Nome in @(
    "auth-service",
    "order-service",
    "product-service",
    "user-service"
)) {
    $Pasta = Join-Path $App $Nome

    if (Test-Path $Pasta -PathType Container) {
        Write-Host "OK: $Nome" -ForegroundColor Green

        VerificarArquivo "$Nome/app.py" (Join-Path $Pasta "app.py")
        VerificarArquivo "$Nome/Dockerfile" (Join-Path $Pasta "Dockerfile")
        VerificarArquivo "$Nome/requirements.txt" (Join-Path $Pasta "requirements.txt")

        if (Test-Path (Join-Path $Pasta ".env")) {
            Write-Host "ENV LOCAL PRESENTE: $Nome"
        }
        else {
            Write-Host "ENV PENDENTE: $Nome" -ForegroundColor Yellow
            $Avisos++
        }
    }
    else {
        Write-Host "AUSENTE: $Nome" -ForegroundColor Red
        $Falhas++
    }
}

Write-Host "`n===== DOCKER =====" -ForegroundColor Cyan

VerificarArquivo "Dockerfile principal" (Join-Path $App "Dockerfile")
VerificarArquivo "docker-compose.yml" (Join-Path $App "docker-compose.yml")
VerificarArquivo "docker-compose.override.yml" (Join-Path $App "docker-compose.override.yml")
VerificarArquivo "MongoDB Dockerfile" (Join-Path $App "mongo\Dockerfile")

Write-Host "`n===== GITHUB ACTIONS =====" -ForegroundColor Cyan

$Workflows = Join-Path $Repo ".github\workflows"

foreach ($Nome in @(
    "auth-service.yml",
    "test-microservices.yml",
    "docker-dev.yml",
    "docker-publish.yml",
    "deploy-ecs.yml",
    "deploy-lambda.yml"
)) {
    VerificarArquivo $Nome (Join-Path $Workflows $Nome)
}

Write-Host "`n===== RESULTADO =====" -ForegroundColor Cyan

Write-Host "Arquivos obrigatorios ausentes: $Falhas"
Write-Host "Configuracoes locais pendentes: $Avisos"

if ($Falhas -eq 0) {
    Write-Host "ESTRUTURA VALIDADA" -ForegroundColor Green
}
else {
    Write-Host "ESTRUTURA COM PENDENCIAS" -ForegroundColor Yellow
}

Write-Host "Nenhum container executado."
Write-Host "Nenhum arquivo de codigo modificado."
Write-Host "Nenhuma publicacao realizada."

if ($Falhas -gt 0) {
    exit 1
}
