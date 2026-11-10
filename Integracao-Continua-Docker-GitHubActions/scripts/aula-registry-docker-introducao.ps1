& {
    $ErrorActionPreference = "Stop"

    $Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"
    Set-Location $Projeto

    $Origem = "alura-cicd-auth-service:1.0"
    $Destino = "alura-cicd-auth-service:registry-estudo"

    Write-Host "`n===== VERSAO DO DOCKER =====" -ForegroundColor Cyan

    docker version --format '{{.Server.Version}}'

    if ($LASTEXITCODE -ne 0) {
        throw "Docker Engine indisponivel."
    }

    Write-Host "`n===== IMAGEM ORIGINAL =====" -ForegroundColor Cyan

    $IdOrigem = docker image inspect $Origem --format '{{.Id}}'

    if ($LASTEXITCODE -ne 0) {
        throw "Imagem original nao encontrada. Nenhuma imagem sera criada."
    }

    Write-Host "IMAGEM ENCONTRADA: $Origem" -ForegroundColor Green

    Write-Host "`n===== VERSIONAMENTO LOCAL =====" -ForegroundColor Cyan

    $Tags = @(docker image ls --format '{{.Repository}}:{{.Tag}}')
    if ($LASTEXITCODE -ne 0) { throw "Falha ao listar imagens Docker." }

    if ($Tags -contains $Destino) {
        $IdDestino = docker image inspect $Destino --format '{{.Id}}'
        if ($LASTEXITCODE -ne 0) { throw "Falha ao inspecionar tag existente." }
        if ($IdDestino -ne $IdOrigem) {
            throw "A tag de estudo ja pertence a outra imagem. Preservada."
        }

        Write-Host "TAG EXISTENTE PRESERVADA" -ForegroundColor Green
    }
    else {
        docker image tag $Origem $Destino

        if ($LASTEXITCODE -ne 0) {
            throw "Falha ao criar etiqueta local."
        }

        Write-Host "NOVA TAG LOCAL CRIADA" -ForegroundColor Green
    }

    Write-Host "`n===== VERIFICACAO FINAL =====" -ForegroundColor Cyan

    $IdFinal = docker image inspect $Destino --format '{{.Id}}'

    if ($LASTEXITCODE -ne 0 -or $IdFinal -ne $IdOrigem) {
        throw "Validacao da tag falhou."
    }

    docker image ls alura-cicd-auth-service

    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao listar imagens."
    }

    Write-Host "`n===== AULA VALIDADA =====" -ForegroundColor Green
    Write-Host "Imagem original preservada."
    Write-Host "Duas tags apontam para a mesma imagem."
    Write-Host "Nenhuma imagem enviada para registry."
    Write-Host "Nenhum container iniciado ou removido."
    Write-Host "Nenhum commit, push ou deploy."
}
