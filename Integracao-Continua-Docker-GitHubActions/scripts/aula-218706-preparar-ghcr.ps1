& {
    $ErrorActionPreference = "Stop"

    $Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"

    $Origem = "alura-cicd-user-service:1.0"

    $Destino = "ghcr.io/rafaelaale/docker-automation/user-service:1.0"

    Set-Location $Projeto

    Write-Host "`n===== DOCKER ENGINE =====" -ForegroundColor Cyan

    docker version --format '{{.Server.Version}}'

    if ($LASTEXITCODE -ne 0) {
        throw "Docker Engine indisponivel."
    }

    Write-Host "`n===== IMAGENS DISPONIVEIS =====" -ForegroundColor Cyan

    $Tags = @(
        docker image ls --format '{{.Repository}}:{{.Tag}}'
    )

    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao listar imagens."
    }

    if ($Tags -notcontains $Origem) {
        throw "Imagem original nao encontrada. Nenhuma imagem foi criada."
    }

    Write-Host "IMAGEM ORIGINAL ENCONTRADA" -ForegroundColor Green

    Write-Host "`n===== IDENTIFICANDO IMAGEM =====" -ForegroundColor Cyan

    $IdOrigem = @(
        docker image inspect $Origem --format '{{.Id}}'
    )

    if ($LASTEXITCODE -ne 0 -or $IdOrigem.Count -eq 0) {
        throw "Falha ao identificar imagem original."
    }

    $IdOrigem = $IdOrigem[0].Trim()

    Write-Host "ORIGEM: $Origem"
    Write-Host "ID: $IdOrigem"

    Write-Host "`n===== CRIANDO TAG LOCAL GHCR =====" -ForegroundColor Cyan

    if ($Tags -contains $Destino) {
        $IdExistente = @(
            docker image inspect $Destino --format '{{.Id}}'
        )

        if ($LASTEXITCODE -ne 0 -or $IdExistente.Count -eq 0) {
            throw "Falha ao verificar etiqueta existente."
        }

        if ($IdExistente[0].Trim() -ne $IdOrigem) {
            throw "Etiqueta ja pertence a outra imagem. Preservada."
        }

        Write-Host "TAG EXISTENTE PRESERVADA" -ForegroundColor Green
    }
    else {
        docker image tag $Origem $Destino

        if ($LASTEXITCODE -ne 0) {
            throw "Falha ao criar etiqueta local."
        }

        Write-Host "TAG GHCR LOCAL CRIADA" -ForegroundColor Green
    }

    Write-Host "`n===== VALIDANDO ETIQUETA =====" -ForegroundColor Cyan

    $IdFinal = @(
        docker image inspect $Destino --format '{{.Id}}'
    )

    if ($LASTEXITCODE -ne 0 -or $IdFinal.Count -eq 0) {
        throw "Falha ao validar etiqueta."
    }

    if ($IdFinal[0].Trim() -ne $IdOrigem) {
        throw "A etiqueta aponta para uma imagem diferente."
    }

    Write-Host "MESMA IMAGEM CONFIRMADA" -ForegroundColor Green

    docker image ls ghcr.io/rafaelaale/docker-automation/user-service

    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao listar etiqueta GHCR."
    }

    Write-Host "`n===== RESULTADO FINAL =====" -ForegroundColor Green

    Write-Host "IMAGEM ORIGINAL: $Origem"
    Write-Host "TAG GHCR LOCAL: $Destino"

    Write-Host "PREPARACAO GHCR VALIDADA."
    Write-Host "Nenhum login realizado."
    Write-Host "Nenhuma imagem publicada."
    Write-Host "Nenhum container alterado."
    Write-Host "Nenhum commit, push ou deploy."
}
