& {
    $ErrorActionPreference = "Stop"

    $Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"
    $Aulas = Join-Path $Projeto "aulas"

    $Notas = Join-Path $Aulas "aula-218708-aws-ecs-fargate.txt"
    $Base = Join-Path $Aulas "docker-compose-microservicos-aula.yml"
    $Override = Join-Path $Aulas "docker-compose-mongodb-aula.override.yml"

    Set-Location $Projeto

    Write-Host "`n===== VALIDANDO CONCEITOS ECS =====" -ForegroundColor Cyan

    if (!(Test-Path $Notas -PathType Leaf)) {
        throw "Anotacoes da aula nao encontradas."
    }

    $Texto = Get-Content -LiteralPath $Notas -Raw

    $Conceitos = @(
        "AMAZON ECS",
        "CLUSTER ECS",
        "TASK DEFINITION",
        "TASK",
        "ECS SERVICE",
        "AWS FARGATE",
        "ECS COM EC2",
        "ECS COM FARGATE",
        "AMAZON ECR",
        "CPU",
        "MEMORIA",
        "SEGURANCA"
    )

    foreach ($Conceito in $Conceitos) {
        if ($Texto.IndexOf($Conceito, [StringComparison]::OrdinalIgnoreCase) -lt 0) {
            throw "Conceito ausente: $Conceito"
        }

        Write-Host "VALIDADO: $Conceito" -ForegroundColor Green
    }

    Write-Host "`n===== VALIDANDO NOSSA APLICACAO =====" -ForegroundColor Cyan

    foreach ($Arquivo in @($Base, $Override)) {
        if (!(Test-Path $Arquivo -PathType Leaf)) {
            throw "Compose nao encontrado: $Arquivo"
        }
    }

    docker compose -p alura-cicd-compose-aula `
        -f $Base `
        -f $Override `
        config --quiet

    if ($LASTEXITCODE -ne 0) {
        throw "Configuracao Docker Compose invalida."
    }

    $Servicos = @(
        docker compose -p alura-cicd-compose-aula `
            -f $Base `
            -f $Override `
            config --services
    )

    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao consultar os servicos."
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

    Write-Host "Conceitos ECS e Fargate documentados."
    Write-Host "Cinco servicos identificados no Compose."
    Write-Host "Nenhum recurso AWS criado."
    Write-Host "Nenhum container local alterado."
    Write-Host "Nenhum commit, push ou deploy."
}
