& {
    $ErrorActionPreference = "Stop"

    $Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"

    $Origem = "alura-cicd-auth-service:1.0"
    $Destino = "ghcr.io/estudo-ghcr/alura-auth-service:1.0"

    Set-Location $Projeto

    Write-Host "`n===== DOCKER ENGINE =====" -ForegroundColor Cyan

    docker version --format '{{.Server.Version}}'

    if ($LASTEXITCODE -ne 0) {
        throw "Docker Engine indisponivel."
    }

    Write-Host "`n===== VERIFICANDO IMAGEM ORIGINAL =====" -ForegroundColor Cyan

    $IdOrigem = @(
        docker image inspect $Origem --format '{{.Id}}'
    )

    if ($LASTEXITCODE -ne 0 -or $IdOrigem.Count -eq 0) {
        throw "Imagem original nao encontrada."
    }

    $IdOrigem = $IdOrigem[0].Trim()

    Write-Host "IMAGEM ORIGINAL CONFIRMADA" -ForegroundColor Green

    Write-Host "`n===== VERIFICANDO TAGS EXISTENTES =====" -ForegroundColor Cyan

    $Tags = @(
        docker image ls --format '{{.Repository}}:{{.Tag}}'
    )

    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao consultar imagens."
    }

    if ($Tags -contains $Destino) {
        $IdExistente = @(
            docker image inspect $Destino --format '{{.Id}}'
        )

        if ($LASTEXITCODE -ne 0 -or $IdExistente.Count -eq 0) {
            throw "Falha ao verificar a tag existente."
        }

        if ($IdExistente[0].Trim() -ne $IdOrigem) {
            throw "Tag existente pertence a outra imagem. Preservada."
        }

        Write-Host "TAG GHCR EXISTENTE PRESERVADA" -ForegroundColor Green
    }
    else {
        Write-Host "`n===== CRIANDO TAG GHCR LOCAL =====" -ForegroundColor Cyan

        docker image tag $Origem $Destino

        if ($LASTEXITCODE -ne 0) {
            throw "Falha ao criar tag local."
        }

        Write-Host "TAG GHCR LOCAL CRIADA" -ForegroundColor Green
    }

    Write-Host "`n===== VALIDANDO IMAGEM =====" -ForegroundColor Cyan

    $IdFinal = @(
        docker image inspect $Destino --format '{{.Id}}'
    )

    if ($LASTEXITCODE -ne 0 -or $IdFinal.Count -eq 0) {
        throw "Falha na verificacao final."
    }

    if ($IdFinal[0].Trim() -ne $IdOrigem) {
        throw "Os identificadores das imagens sao diferentes."
    }

    Write-Host "MESMA IMAGEM CONFIRMADA" -ForegroundColor Green

    docker image ls ghcr.io/estudo-ghcr/alura-auth-service

    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao listar imagem GHCR."
    }

    Write-Host "`n===== AULA VALIDADA =====" -ForegroundColor Green

    Write-Host "Tag GHCR preparada localmente."
    Write-Host "Imagem original preservada."
    Write-Host "Nenhuma imagem publicada."
    Write-Host "Nenhum container alterado."
    Write-Host "Nenhum commit, push ou deploy."
}
