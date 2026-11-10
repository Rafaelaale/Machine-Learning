& {
    $ErrorActionPreference = "Stop"

    $Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"
    $Repositorio = Join-Path $Projeto "docker-automation"

    $Workflow = Join-Path $Projeto "aulas\seguranca-pipelines\docker-security-rascunho.yml"
    $Notas = Join-Path $Projeto "aulas\seguranca-pipelines\aula-218713-seguranca-pipelines.txt"

    Write-Host "`n===== VALIDANDO ARQUIVOS =====" -ForegroundColor Cyan

    foreach ($Arquivo in @($Workflow, $Notas)) {
        if (!(Test-Path -LiteralPath $Arquivo -PathType Leaf)) {
            throw "Arquivo ausente: $Arquivo"
        }

        Write-Host "ARQUIVO ENCONTRADO: $([IO.Path]::GetFileName($Arquivo))" -ForegroundColor Green
    }

    $Texto = [IO.File]::ReadAllText($Workflow)

    Write-Host "`n===== VALIDANDO BOAS PRATICAS =====" -ForegroundColor Cyan

    $Termos = @(
        'if: ${{ false }}',
        "permissions:",
        "contents: read",
        "actions/checkout@v4",
        "docker compose version",
        "::add-mask::",
        'secrets.MONGO_URI',
        'secrets.SECRET_KEY',
        "umask 077",
        "auth-service",
        "user-service",
        "order-service",
        "product-service",
        "docker compose",
        "mongosh --quiet",
        "if: always()",
        "down --remove-orphans"
    )

    foreach ($Termo in $Termos) {
        if (!$Texto.Contains($Termo)) {
            throw "Configuracao ausente: $Termo"
        }

        Write-Host "VALIDADO: $Termo" -ForegroundColor Green
    }

    if ($Texto.Contains("down --volumes")) {
        throw "Remocao de volumes encontrada no workflow."
    }

    if ($Workflow -match '[\\/]\.github[\\/]workflows[\\/]') {
        throw "Rascunho esta em pasta de workflow ativo."
    }

    Write-Host "`n===== AUDITORIA GIT SOMENTE LEITURA =====" -ForegroundColor Cyan

    if (Get-Command git -ErrorAction SilentlyContinue) {
        $Rastreado = @(
            git -C $Repositorio ls-files -- "burguer-app/auth-service/.env"
        )

        if ($LASTEXITCODE -ne 0) {
            throw "Nao foi possivel consultar os arquivos rastreados."
        }

        if ($Rastreado.Count -gt 0) {
            Write-Host "ALERTA: auth-service/.env ESTA RASTREADO PELO GIT." -ForegroundColor Yellow
            Write-Host "Corrigir antes de qualquer publicacao." -ForegroundColor Yellow
        }
        else {
            Write-Host "auth-service/.env NAO aparece entre os arquivos rastreados." -ForegroundColor Green
        }
    }
    else {
        Write-Host "Git nao disponivel. Auditoria de rastreamento pendente." -ForegroundColor Yellow
    }

    Write-Host "`n===== RESULTADO FINAL =====" -ForegroundColor Green

    Write-Host "Elementos de seguranca encontrados no rascunho."
    Write-Host "Nenhuma verificacao remota executada."
    Write-Host "Workflow permanece desativado."
    Write-Host "Nenhum arquivo .env modificado."
    Write-Host "Nenhum container ou volume alterado."
    Write-Host "Nenhum codigo publicado."
    Write-Host "Nenhum deploy executado."
}
