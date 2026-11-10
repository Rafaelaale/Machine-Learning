& {
    $ErrorActionPreference = "Stop"

    $Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"

    $Origem = "alura-cicd-auth-service:1.0"
    $Destino = "dockerhub-estudo/alura:1.0"

    Set-Location $Projeto

    Write-Host "`n===== DOCKER ENGINE =====" -ForegroundColor Cyan

    docker version --format '{{.Server.Version}}'

    if ($LASTEXITCODE -ne 0) {
        throw "Docker Engine indisponivel."
    }

    Write-Host "`n===== VERIFICANDO IMAGEM ORIGINAL =====" -ForegroundColor Cyan

    $IdOrigem = @(docker image inspect $Origem --format '{{.Id}}')

    if ($LASTEXITCODE -ne 0 -or $IdOrigem.Count -eq 0) {
        throw "Imagem original nao encontrada."
    }

    $IdOrigem = $IdOrigem[0].Trim()

    Write-Host "ORIGEM CONFIRMADA: $Origem" -ForegroundColor Green

    Write-Host "`n===== CONSULTANDO ETIQUETAS EXISTENTES =====" -ForegroundColor Cyan

    $Etiquetas = @(
        docker image ls --format '{{.Repository}}:{{.Tag}}'
    )

    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao consultar imagens Docker."
    }

    if ($Etiquetas -contains $Destino) {
        $IdExistente = @(
            docker image inspect $Destino --format '{{.Id}}'
        )

        if ($LASTEXITCODE -ne 0 -or $IdExistente.Count -eq 0) {
            throw "Falha ao consultar a etiqueta existente."
        }

        if ($IdExistente[0].Trim() -ne $IdOrigem) {
            throw "A etiqueta ja pertence a outra imagem. Preservada."
        }

        Write-Host "ETIQUETA EXISTENTE PRESERVADA" -ForegroundColor Green
    }
    else {
        Write-Host "`n===== CRIANDO TAG LOCAL =====" -ForegroundColor Cyan

        docker image tag $Origem $Destino

        if ($LASTEXITCODE -ne 0) {
            throw "Falha ao criar etiqueta local."
        }

        Write-Host "NOVA TAG LOCAL CRIADA" -ForegroundColor Green
    }

    Write-Host "`n===== VERIFICACAO FINAL =====" -ForegroundColor Cyan

    $IdFinal = @(
        docker image inspect $Destino --format '{{.Id}}'
    )

    if ($LASTEXITCODE -ne 0 -or $IdFinal.Count -eq 0) {
        throw "Falha na verificacao final."
    }

    if ($IdFinal[0].Trim() -ne $IdOrigem) {
        throw "Identificadores de imagem diferentes."
    }

    Write-Host "ORIGEM: $Origem"
    Write-Host "TAG LOCAL: $Destino"

    Write-Host "MESMA IMAGEM CONFIRMADA" -ForegroundColor Green

    docker image ls dockerhub-estudo/alura

    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao listar a imagem preparada."
    }

    Write-Host "`n===== AULA VALIDADA =====" -ForegroundColor Green

    Write-Host "Etiqueta local preparada para estudo."
    Write-Host "Nenhuma autenticacao no Docker Hub."
    Write-Host "Nenhuma imagem enviada para a internet."
    Write-Host "Nenhum container modificado."
    Write-Host "Nenhum commit, push ou deploy."
}
