$ErrorActionPreference = "Stop"
$App = "F:\Projetos\Docker-GitHubActions-CI-CD\docker-automation\burguer-app"
$Compose = Join-Path $App "docker-compose.yml"

Write-Host "===== VERSAO DO COMPOSE ====="
docker compose version
if ($LASTEXITCODE -ne 0) { throw "Docker Compose indisponivel." }

Write-Host "===== VALIDANDO YAML ====="
docker compose -f $Compose config --quiet
if ($LASTEXITCODE -ne 0) { throw "Configuracao YAML invalida." }

Write-Host "===== SERVICOS DEFINIDOS ====="
docker compose -f $Compose config --services
if ($LASTEXITCODE -ne 0) { throw "Falha ao listar servicos." }

Write-Host "===== VALIDACAO CONCLUIDA ====="
Write-Host "Nenhum conteiner iniciado ou removido."
