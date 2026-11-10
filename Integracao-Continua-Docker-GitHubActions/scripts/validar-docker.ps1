$ErrorActionPreference = "Stop"
Write-Host "===== DOCKER ENGINE ====="
docker info --format '{{.ServerVersion}}'
if ($LASTEXITCODE -ne 0) { throw "Docker indisponivel." }
Write-Host "===== DOCKER COMPOSE ====="
docker compose version
if ($LASTEXITCODE -ne 0) { throw "Docker Compose indisponivel." }
Write-Host "===== CONTEINERES ====="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
Write-Host "===== MONGODB DA TRILHA ====="
docker ps --filter "name=^/alura-cicd-mongodb$" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
Write-Host "VALIDACAO CONCLUIDA"
