$ErrorActionPreference = "Stop"
$Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"
$Base = Join-Path $Projeto "aulas\docker-compose-microservicos-aula.yml"
$Override = Join-Path $Projeto "aulas\docker-compose-mongodb-aula.override.yml"
docker compose -p alura-cicd-compose-aula -f $Base -f $Override config --quiet
if ($LASTEXITCODE -ne 0) { throw "Falha no Compose." }
docker compose -p alura-cicd-compose-aula -f $Base -f $Override config --services
if ($LASTEXITCODE -ne 0) { throw "Falha na listagem de servicos." }
Write-Host "COMPOSE MONGODB VALIDADO" -ForegroundColor Green
