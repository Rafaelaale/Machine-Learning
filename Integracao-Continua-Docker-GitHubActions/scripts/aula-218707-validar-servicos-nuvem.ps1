& {
    $ErrorActionPreference = "Stop"

    $Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"
    $Aulas = Join-Path $Projeto "aulas"

    $Notas = Join-Path $Aulas "aula-218707-servicos-nuvem-containers.txt"
    $Base = Join-Path $Aulas "docker-compose-microservicos-aula.yml"
    $Override = Join-Path $Aulas "docker-compose-mongodb-aula.override.yml"

    Set-Location $Projeto

    Write-Host "`n===== VALIDANDO TEORIA =====" -ForegroundColor Cyan

    if (!(Test-Path $Notas)) {
        throw "Notas da aula nao encontradas."
    }

    $Texto = Get-Content $Notas -Raw

    $Conceitos = @(
        "ECS",
        "EKS",
        "FARGATE",
        "AKS",
        "ACI",
        "AZURE CONTAINER APPS",
        "GKE",
        "CLOUD RUN",
        "CLOUD FUNCTIONS",
        "DIGITALOCEAN",
        "HEROKU",
        "IBM CLOUD"
    )

    foreach ($Conceito in $Conceitos) {
        if (!$Texto.Contains($Conceito)) {
            throw "Conceito ausente: $Conceito"
        }

        Write-Host "VALIDADO: $Conceito" -ForegroundColor Green
    }

    Write-Host "`n===== VERIFICANDO NOSSO COMPOSE =====" -ForegroundColor Cyan

    docker compose -p alura-cicd-compose-aula `
        -f $Base `
        -f $Override `
        config --quiet

    if ($LASTEXITCODE -ne 0) {
        throw "Falha na configuracao Docker Compose."
    }

    $Servicos = @(
        docker compose -p alura-cicd-compose-aula `
            -f $Base `
            -f $Override `
            config --services
    )

    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao consultar servicos."
    }

    foreach ($Nome in @(
        "auth-service",
        "user-service",
        "order-service",
        "product-service",
        "mongo"
    )) {
        if ($Servicos -notcontains $Nome) {
            throw "Servico ausente: $Nome"
        }

        Write-Host "SERVICO IDENTIFICADO: $Nome" -ForegroundColor Green
    }

    Write-Host "`n===== REVISAO CONCLUIDA =====" -ForegroundColor Green

    Write-Host "Conceitos de computacao em nuvem documentados."
    Write-Host "Cinco servicos identificados no Compose."
    Write-Host "Nenhum container alterado."
    Write-Host "Nenhum recurso de nuvem criado."
    Write-Host "Nenhum commit, push ou deploy."
}
