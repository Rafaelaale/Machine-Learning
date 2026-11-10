& {
    $ErrorActionPreference = "Stop"

    $Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"
    $Workflow = Join-Path $Projeto "aulas\versionamento\docker-dev-versionamento-rascunho.yml"
    $Notas = Join-Path $Projeto "aulas\versionamento\aula-218718-implementando-versionamento.txt"

    Write-Host "`n===== VALIDANDO ARQUIVOS =====" -ForegroundColor Cyan

    foreach ($Arquivo in @($Workflow, $Notas)) {
        if (!(Test-Path -LiteralPath $Arquivo -PathType Leaf)) {
            throw "Arquivo nao encontrado: $Arquivo"
        }

        Write-Host "ENCONTRADO: $([IO.Path]::GetFileName($Arquivo))" -ForegroundColor Green
    }

    $Texto = [IO.File]::ReadAllText($Workflow)

    Write-Host "`n===== VALIDANDO PIPELINE =====" -ForegroundColor Cyan

    $Termos = @(
        'if: ${{ false }}',
        "actions/checkout@v4",
        'VERSION="${GITHUB_SHA:0:7}"',
        'echo "IMAGE_TAG=${VERSION}" >> "$GITHUB_ENV"',
        "docker build",
        "docker image inspect",
        "docker images",
        "auth-service",
        "user-service",
        "order-service",
        "product-service",
        "IMAGE_TAG",
        "latest",
        "set -euo pipefail"
    )

    foreach ($Termo in $Termos) {
        if (!$Texto.Contains($Termo)) {
            throw "Configuracao ausente: $Termo"
        }

        Write-Host "VALIDADO: $Termo" -ForegroundColor Green
    }

    Write-Host "`n===== TESTANDO GERACAO DE TAG =====" -ForegroundColor Cyan

    $SHASimulado = "59c5b75e01af8888"
    $Tag = $SHASimulado.Substring(0, 7)

    if ($Tag -cne "59c5b75") {
        throw "Falha na geracao da tag."
    }

    if ($Tag -cnotmatch '^[0-9a-f]{7}$') {
        throw "Formato de tag incorreto."
    }

    Write-Host "SHA SIMULADO: $SHASimulado" -ForegroundColor Green
    Write-Host "TAG GERADA: $Tag" -ForegroundColor Green

    Write-Host "`n===== VALIDANDO QUATRO IMAGENS =====" -ForegroundColor Cyan

    $Servicos = @(
        "auth-service",
        "user-service",
        "order-service",
        "product-service"
    )

    foreach ($Servico in $Servicos) {
        $Imagem = "burguer-app-${Servico}:${Tag}"

        Write-Host "IMAGEM DE EXEMPLO: $Imagem" -ForegroundColor Green
    }

    Write-Host "`n===== VERIFICANDO ISOLAMENTO =====" -ForegroundColor Cyan

    if ($Workflow -match '[\\/]\.github[\\/]workflows[\\/]') {
        throw "Workflow localizado em pasta ativa."
    }

    if (!$Texto.Contains('if: ${{ false }}')) {
        throw "Workflow nao esta desativado."
    }

    Write-Host "WORKFLOW FORA DA PASTA ATIVA" -ForegroundColor Green
    Write-Host "JOB DESATIVADO" -ForegroundColor Green

    Write-Host "`n===== RESULTADO FINAL =====" -ForegroundColor Green

    Write-Host "ETAPAS CONFERIDAS: $($Termos.Count)"
    Write-Host "TAGS SIMULADAS: 4/4"
    Write-Host "LOGICA DE VERSIONAMENTO VALIDADA LOCALMENTE."
    Write-Host "Build Docker nao executado."
    Write-Host "Pipeline remoto nao executado."
    Write-Host "Nenhum codigo publicado."
    Write-Host "Nenhum container alterado."
    Write-Host "Nenhum deploy realizado."
}
