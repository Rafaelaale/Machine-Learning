$ErrorActionPreference = "Stop"
$Nome = "alura-aula-nginx-comandos"

Write-Host "`n===== DOCKER ENGINE =====" -ForegroundColor Cyan
docker info --format "{{.ServerVersion}}"
if ($LASTEXITCODE -ne 0) { throw "Docker indisponivel." }

Write-Host "`n===== PESQUISANDO IMAGENS UBUNTU =====" -ForegroundColor Cyan
docker search ubuntu --limit 5
if ($LASTEXITCODE -ne 0) { Write-Warning "Pesquisa online indisponivel." }

Write-Host "`n===== VERIFICANDO IMAGEM UBUNTU =====" -ForegroundColor Cyan
$Ubuntu = @(docker image ls ubuntu:latest --format "{{.Repository}}")
if ($Ubuntu.Count -eq 0) {
    docker pull ubuntu:latest
    if ($LASTEXITCODE -ne 0) { throw "Falha ao baixar Ubuntu." }
}

Write-Host "`n===== VERIFICANDO IMAGEM NGINX =====" -ForegroundColor Cyan
$Nginx = @(docker image ls nginx:latest --format "{{.Repository}}")
if ($Nginx.Count -eq 0) {
    docker pull nginx:latest
    if ($LASTEXITCODE -ne 0) { throw "Falha ao baixar Nginx." }
}

Write-Host "`n===== IMAGENS DISPONIVEIS =====" -ForegroundColor Cyan
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

Write-Host "`n===== EXECUTANDO UBUNTU =====" -ForegroundColor Cyan
docker run --rm ubuntu:latest sh -c "ls; mkdir -p /tmp/teste; ls /tmp"
if ($LASTEXITCODE -ne 0) { throw "Falha no Ubuntu." }

Write-Host "`n===== CONTEINERES ATIVOS =====" -ForegroundColor Cyan
docker ps --format "table {{.Names}}\t{{.Status}}"

Write-Host "`n===== PREPARANDO NGINX DA AULA =====" -ForegroundColor Cyan
$Existente = @(docker ps -a --filter "name=^/$Nome$" --format "{{.Names}}")
if ($Existente.Count -eq 0) {
    $Porta = $null
    foreach ($P in 18080..18089) {
        $Ocupada = Get-NetTCPConnection -LocalPort $P -State Listen -ErrorAction SilentlyContinue
        if (-not $Ocupada) { $Porta = $P; break }
    }
    if ($null -eq $Porta) { throw "Nenhuma porta livre entre 18080 e 18089." }
    docker run -d --name $Nome -p "127.0.0.1:${Porta}:80" nginx:latest
    if ($LASTEXITCODE -ne 0) { throw "Falha ao criar Nginx." }
    Write-Host "NGINX CRIADO NA PORTA $Porta" -ForegroundColor Green
}
else {
    Write-Host "Conteiner da aula ja existe. Preservado."
}

Write-Host "`n===== VERIFICANDO NGINX =====" -ForegroundColor Cyan
docker ps -a --filter "name=^/$Nome$" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

Write-Host "`n===== PORTA DO NGINX =====" -ForegroundColor Cyan
docker port $Nome

Write-Host "`n===== CONTEINERES EM TODOS OS ESTADOS =====" -ForegroundColor Cyan
docker ps -a --format "table {{.Names}}\t{{.Status}}"

Write-Host "`n===== AULA EXECUTADA =====" -ForegroundColor Green
Write-Host "Ubuntu testado."
Write-Host "Nginx criado ou preservado."
Write-Host "Outros conteineres nao foram alterados."
Write-Host "Nenhuma publicacao realizada."
