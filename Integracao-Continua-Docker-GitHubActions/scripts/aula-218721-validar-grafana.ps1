& {
    $ErrorActionPreference = "Stop"

    $Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"
    $Aulas = Join-Path $Projeto "aulas"

    $Pasta = Join-Path $Aulas "observabilidade\grafana"

    $Compose = Join-Path $Aulas "grafana-compose-aula.override.yml"
    $ComposePrometheus = Join-Path $Aulas "prometheus-compose-aula.override.yml"

    $Datasource = Join-Path $Pasta "provisioning\datasources\prometheus.yml"
    $Provider = Join-Path $Pasta "provisioning\dashboards\default.yml"
    $Dashboard = Join-Path $Pasta "dashboards\microservicos.json"

    $Prometheus = Join-Path $Aulas "observabilidade\prometheus.yml"

    Write-Host "`n===== VALIDANDO ARQUIVOS =====" -ForegroundColor Cyan

    foreach ($Arquivo in @(
        $Compose,
        $ComposePrometheus,
        $Datasource,
        $Provider,
        $Dashboard,
        $Prometheus
    )) {
        if (!(Test-Path -LiteralPath $Arquivo -PathType Leaf)) {
            throw "Arquivo nao encontrado: $Arquivo"
        }

        Write-Host "ENCONTRADO: $([IO.Path]::GetFileName($Arquivo))" -ForegroundColor Green
    }

    Write-Host "`n===== VALIDANDO DOCKER COMPOSE =====" -ForegroundColor Cyan

    $TextoCompose = [IO.File]::ReadAllText($Compose)

    $TermosCompose = @(
        "grafana:",
        "grafana/grafana:",
        "127.0.0.1:13000:3000",
        "GF_SECURITY_ADMIN_USER",
        "GF_SECURITY_ADMIN_PASSWORD",
        "GF_USERS_ALLOW_SIGN_UP",
        "GF_AUTH_ANONYMOUS_ENABLED",
        "depends_on:",
        "prometheus",
        "alura-cicd-aula-rede",
        "prometheus.yml",
        "./observabilidade/grafana/dashboards:/var/lib/grafana/dashboards:ro"
    )

    foreach ($Termo in $TermosCompose) {
        if (!$TextoCompose.Contains($Termo)) {
            throw "Configuracao ausente: $Termo"
        }

        Write-Host "VALIDADO: $Termo" -ForegroundColor Green
    }

    Write-Host "`n===== VALIDANDO FONTE DE DADOS =====" -ForegroundColor Cyan

    $TextoDatasource = [IO.File]::ReadAllText($Datasource)

    foreach ($Termo in @(
        "apiVersion: 1",
        "type: prometheus",
        "uid: prometheus-local",
        "http://prometheus:9090",
        "isDefault: true"
    )) {
        if (!$TextoDatasource.Contains($Termo)) {
            throw "Datasource incompleto: $Termo"
        }

        Write-Host "VALIDADO: $Termo" -ForegroundColor Green
    }

    Write-Host "`n===== VALIDANDO DASHBOARD =====" -ForegroundColor Cyan

    $Dados = Get-Content -LiteralPath $Dashboard -Raw |
        ConvertFrom-Json

    if ($Dados.uid -ne "alura-burger-observabilidade") {
        throw "UID do dashboard incorreto."
    }

    if (@($Dados.panels).Count -ne 3) {
        throw "Quantidade de paineis incorreta."
    }

    $Consultas = @(
        "process_cpu_seconds_total",
        "process_open_fds",
        "auth_service_metrics_scrapes_total"
    )

    foreach ($Consulta in $Consultas) {
        $Encontrada = $false

        foreach ($Painel in $Dados.panels) {
            foreach ($Target in $Painel.targets) {
                if ($Target.expr.Contains($Consulta)) {
                    $Encontrada = $true
                }
            }
        }

        if (!$Encontrada) {
            throw "Consulta ausente: $Consulta"
        }

        Write-Host "PROMQL VALIDADA ESTRUTURALMENTE: $Consulta" -ForegroundColor Green
    }

    Write-Host "`n===== VALIDANDO PROVIDER =====" -ForegroundColor Cyan

    $TextoProvider = [IO.File]::ReadAllText($Provider)

    if (!$TextoProvider.Contains("/var/lib/grafana/dashboards")) {
        throw "Diretorio dos dashboards incorreto."
    }

    Write-Host "PROVIDER CONFIGURADO" -ForegroundColor Green

    Write-Host "`n===== CONFERINDO PROMETHEUS =====" -ForegroundColor Cyan

    $TextoPrometheus = [IO.File]::ReadAllText($Prometheus)

    if (!$TextoPrometheus.Contains("auth-service:5000")) {
        throw "Target Auth Service ausente."
    }

    Write-Host "TARGET AUTH SERVICE IDENTIFICADO" -ForegroundColor Green

    Write-Host "`n===== RESULTADO FINAL =====" -ForegroundColor Green

    Write-Host "CONFIGURACAO GRAFANA CONFERIDA."
    Write-Host "DATASOURCE PROMETHEUS CONFERIDO."
    Write-Host "DASHBOARD JSON VALIDO."
    Write-Host "PAINEIS CONFIGURADOS: 3/3"
    Write-Host "INTEGRACAO PREPARADA LOCALMENTE."
    Write-Host "Validacao real de YAML e conexoes ainda pendente."
    Write-Host "Nenhum Docker executado."
    Write-Host "Nenhum container alterado."
    Write-Host "Nenhum codigo publicado."
    Write-Host "Nenhum deploy realizado."
}
