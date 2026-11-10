$ErrorActionPreference = "Stop"

$Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"
Set-Location $Projeto

$Origem = "alura-cicd-auth-service:1.0"
$Estudo = "alura-cicd-auth-service:registry-estudo"

Write-Host "`n===== DOCKER =====" -ForegroundColor Cyan
docker version --format '{{.Server.Version}}'
if ($LASTEXITCODE -ne 0) { throw "Docker indisponivel." }

Write-Host "`n===== IMAGENS LOCAIS =====" -ForegroundColor Cyan
docker image ls alura-cicd-auth-service
if ($LASTEXITCODE -ne 0) { throw "Falha ao listar imagens." }

Write-Host "`n===== VALIDANDO IDENTIFICADORES =====" -ForegroundColor Cyan
$IdOrigem = docker image inspect $Origem --format '{{.Id}}'
if ($LASTEXITCODE -ne 0) { throw "Imagem original nao encontrada." }

$IdEstudo = docker image inspect $Estudo --format '{{.Id}}'
if ($LASTEXITCODE -ne 0) { throw "Tag de estudo nao encontrada." }

if ($IdOrigem.Trim() -ne $IdEstudo.Trim()) {
    throw "As duas tags apontam para imagens diferentes."
}

Write-Host "IMAGENS COM O MESMO ID" -ForegroundColor Green
Write-Host "TAG ORIGINAL: $Origem"
Write-Host "TAG DE ESTUDO: $Estudo"

Write-Host "`n===== AULA VALIDADA =====" -ForegroundColor Green
Write-Host "Docker Hub e GHCR estudados."
Write-Host "Imagens locais verificadas."
Write-Host "Nenhuma imagem publicada."
Write-Host "Nenhum container modificado."
Write-Host "Nenhum commit, push ou deploy."
