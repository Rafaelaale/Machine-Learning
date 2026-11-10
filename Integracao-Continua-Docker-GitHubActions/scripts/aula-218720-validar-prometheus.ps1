& {
    $ErrorActionPreference = "Stop"

    $Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"

    $App = Join-Path $Projeto "docker-automation\burguer-app\auth-service\app.py"
    $Requirements = Join-Path $Projeto "docker-automation\burguer-app\auth-service\requirements.txt"

    $Prometheus = Join-Path $Projeto "aulas\observabilidade\prometheus.yml"
    $Compose = Join-Path $Projeto "aulas\prometheus-compose-aula.override.yml"

    Write-Host "`n===== VALIDANDO ARQUIVOS =====" -ForegroundColor Cyan

    foreach ($Arquivo in @($App, $Requirements, $Prometheus, $Compose)) {
        if (!(Test-Path $Arquivo -PathType Leaf)) {
            throw "Arquivo ausente: $Arquivo"
        }

        Write-Host "ENCONTRADO: $([IO.Path]::GetFileName($Arquivo))" -ForegroundColor Green
    }

    Write-Host "`n===== VALIDANDO FLASK =====" -ForegroundColor Cyan

    $Codigo = [IO.File]::ReadAllText($App)

    foreach ($Termo in @(
        "prometheus_client",
        "Counter",
        "generate_latest",
        "CONTENT_TYPE_LATEST",
        '"/metrics"',
        "auth_service_metrics_scrapes_total"
    )) {
        if (!$Codigo.Contains($Termo)) {
            throw "Implementacao ausente: $Termo"
        }

        Write-Host "VALIDADO: $Termo" -ForegroundColor Green
    }

    if (Get-Command python -ErrorAction SilentlyContinue) {
        python -B -c "import ast,sys; ast.parse(open(sys.argv[1],encoding='utf-8-sig').read()); print('SINTAXE PYTHON APROVADA')" $App

        if ($LASTEXITCODE -ne 0) {
            throw "Erro de sintaxe no app.py."
        }
    }
    else {
        Write-Host "Python indisponivel. Validacao de sintaxe pendente." -ForegroundColor Yellow
    }

    Write-Host "`n===== VALIDANDO DEPENDENCIAS =====" -ForegroundColor Cyan

    $Req = [IO.File]::ReadAllText($Requirements)

    if ($Req -notmatch '(?mi)^\s*prometheus[-_]client\s*[=<>!~]') {
        throw "Dependencia Prometheus nao encontrada."
    }

    Write-Host "PROMETHEUS CLIENT CONFIGURADO" -ForegroundColor Green

    Write-Host "`n===== VALIDANDO PROMETHEUS =====" -ForegroundColor Cyan

    $Config = [IO.File]::ReadAllText($Prometheus)

    foreach ($Termo in @(
        "scrape_interval: 5s",
        'job_name: "auth-service"',
        "auth-service:5000",
        "/metrics"
    )) {
        if (!$Config.Contains($Termo)) {
            throw "Configuracao ausente: $Termo"
        }

        Write-Host "VALIDADO: $Termo" -ForegroundColor Green
    }

    Write-Host "`n===== VALIDANDO COMPOSE =====" -ForegroundColor Cyan

    $ComposeTexto = [IO.File]::ReadAllText($Compose)

    foreach ($Termo in @(
        "prom/prometheus",
        "19090:9090",
        "prometheus.yml",
        "alura-cicd-aula-rede"
    )) {
        if (!$ComposeTexto.Contains($Termo)) {
            throw "Configuracao Compose ausente: $Termo"
        }

        Write-Host "VALIDADO: $Termo" -ForegroundColor Green
    }

    Write-Host "`n===== RESULTADO FINAL =====" -ForegroundColor Green

    Write-Host "INSTRUMENTACAO FLASK CONFERIDA."
    Write-Host "DEPENDENCIA PROMETHEUS CONFERIDA."
    Write-Host "CONFIGURACAO PROMETHEUS CONFERIDA."
    Write-Host "COMPOSE PREPARADO PARA TESTE FUTURO."
    Write-Host "Execucao real do Prometheus ainda pendente."
    Write-Host "Nenhum Docker executado."
    Write-Host "Nenhum codigo publicado."
    Write-Host "Nenhum deploy realizado."
}
