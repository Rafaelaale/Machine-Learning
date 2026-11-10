
    param([string]$Projeto)

    $ErrorActionPreference = "Stop"

    $App = Join-Path $Projeto "docker-automation\burguer-app"
    $Dockerfile = Join-Path $App "Dockerfile"
    $Rede = "alura-cicd-aula-rede"
    $Mongo = "alura-cicd-mongodb"
    $ArquivoEnv = Join-Path $Projeto "aulas\microservicos-local.env"

    $Servicos = @(
        @{ Nome = "auth-service"; Porta = 5000 },
        @{ Nome = "user-service"; Porta = 5001 },
        @{ Nome = "order-service"; Porta = 5002 },
        @{ Nome = "product-service"; Porta = 5003 }
    )

    Set-Location $Projeto

    Write-Host "`n===== 1. VERIFICANDO DOCKER E PROJETO =====" -ForegroundColor Cyan

    docker info --format '{{.ServerVersion}}'
    if ($LASTEXITCODE -ne 0) { throw "Docker indisponivel." }

    if (!(Test-Path $Dockerfile)) {
        throw "Dockerfile principal nao encontrado."
    }

    foreach ($Servico in $Servicos) {
        $Dir = Join-Path $App $Servico.Nome

        foreach ($Nome in @("app.py", "requirements.txt", "Dockerfile")) {
            if (!(Test-Path (Join-Path $Dir $Nome))) {
                throw "Arquivo ausente: $Dir\$Nome"
            }
        }

        Write-Host "OK: $($Servico.Nome)"
    }

    Write-Host "`n===== 2. VERIFICANDO MONGODB LOCAL =====" -ForegroundColor Cyan

    $Estado = docker inspect $Mongo --format '{{.State.Running}}' 2>$null

    if ($LASTEXITCODE -ne 0 -or $Estado -ne "true") {
        throw "MongoDB da trilha nao esta em execucao."
    }

    $Ping = docker exec $Mongo mongosh --quiet --eval 'db.adminCommand({ping:1}).ok'

    if ($LASTEXITCODE -ne 0 -or "$Ping".Trim() -ne "1") {
        throw "MongoDB nao respondeu ao ping."
    }

    Write-Host "MONGODB VALIDADO" -ForegroundColor Green

    Write-Host "`n===== 3. CONFIGURANDO REDE ISOLADA =====" -ForegroundColor Cyan

    $Redes = @(docker network ls --format '{{.Name}}')

    if ($Redes -notcontains $Rede) {
        docker network create $Rede

        if ($LASTEXITCODE -ne 0) {
            throw "Falha ao criar rede Docker."
        }
    }

    $RedesMongo = docker inspect $Mongo --format '{{json .NetworkSettings.Networks}}'

    if (-not ([string]$RedesMongo).Contains('"' + $Rede + '"')) {
        docker network connect $Rede $Mongo

        if ($LASTEXITCODE -ne 0) {
            throw "Falha ao conectar MongoDB a rede da aula."
        }
    }

    Write-Host "REDE CONFIGURADA: $Rede" -ForegroundColor Green

    Write-Host "`n===== 4. CONFIGURANDO AMBIENTE LOCAL =====" -ForegroundColor Cyan

    $Variaveis = @(
        "MONGO_URI=mongodb://alura-cicd-mongodb:27017/burguer_app_db",
        "SECRET_KEY=segredo-local-exclusivo-aula",
        "JWT_SECRET=jwt-local-exclusivo-aula",
        "PYTHONUNBUFFERED=1",
        "PYTHONDONTWRITEBYTECODE=1"
    )

    if (!(Test-Path $ArquivoEnv)) {
        $Variaveis | Set-Content $ArquivoEnv -Encoding UTF8
        Write-Host "AMBIENTE LOCAL CRIADO" -ForegroundColor Green
    }
    else {
        $Atual = Get-Content $ArquivoEnv

        foreach ($Linha in $Variaveis) {
            if ($Atual -notcontains $Linha) {
                throw "Arquivo de ambiente existente difere do esperado: $ArquivoEnv"
            }
        }

        Write-Host "AMBIENTE LOCAL EXISTENTE PRESERVADO"
    }

    Write-Host "`n===== 5. PROTEGENDO ARQUIVOS LOCAIS =====" -ForegroundColor Cyan

    foreach ($Servico in $Servicos) {
        $Dir = Join-Path $App $Servico.Nome
        $Ignore = Join-Path $Dir ".dockerignore"

        $Padroes = @(
            ".env",
            ".env.*",
            ".venv",
            ".venv/",
            "__pycache__/",
            "*.pyc",
            ".git/"
        )

        if (!(Test-Path $Ignore)) {
            $Padroes | Set-Content $Ignore -Encoding UTF8
        }
        else {
            $Existentes = @(Get-Content $Ignore)

            foreach ($Padrao in $Padroes) {
                if ($Existentes -notcontains $Padrao) {
                    Add-Content $Ignore $Padrao
                }
            }
        }

        Write-Host "DOCKERIGNORE: $($Servico.Nome)"
    }

    Write-Host "`n===== 6. VERIFICANDO PORTAS =====" -ForegroundColor Cyan

    $Inicio = $null

    foreach ($Base in @(5000, 15000, 16000)) {
        $Livre = $true

        foreach ($P in $Base..($Base + 3)) {
            if (Get-NetTCPConnection -LocalPort $P -State Listen -ErrorAction SilentlyContinue) {
                $Livre = $false
                break
            }
        }

        if ($Livre) {
            $Inicio = $Base
            break
        }
    }

    if ($null -eq $Inicio) {
        throw "Nenhum grupo de quatro portas disponivel."
    }

    Write-Host "PORTAS DISPONIVEIS: $Inicio a $($Inicio + 3)"

    if ($Inicio -ne 5000) {
        Write-Warning "Portas alternativas: links fixos da aplicacao podem precisar de ajuste."
    }

    Write-Host "`n===== 7. CONSTRUINDO QUATRO IMAGENS =====" -ForegroundColor Cyan

    foreach ($Servico in $Servicos) {
        $Nome = $Servico.Nome
        $Dir = Join-Path $App $Nome
        $Imagem = "alura-cicd-${Nome}:1.0"

        Write-Host "`nBUILD: $Imagem" -ForegroundColor Yellow

        Push-Location $Dir

        try {
            docker build --pull=false -t $Imagem -f ../Dockerfile .

            if ($LASTEXITCODE -ne 0) {
                throw "Falha no build: $Nome"
            }
        }
        finally {
            Pop-Location
        }

        Write-Host "IMAGEM CRIADA: $Imagem" -ForegroundColor Green
    }

    Write-Host "`n===== 8. EXECUTANDO MICROSSERVICOS =====" -ForegroundColor Cyan

    $Falhas = 0
    $Resultados = @()

    for ($Indice = 0; $Indice -lt $Servicos.Count; $Indice++) {
        $Servico = $Servicos[$Indice]
        $Nome = $Servico.Nome
        $Interna = $Servico.Porta
        $Externa = $Inicio + $Indice

        $Imagem = "alura-cicd-${Nome}:1.0"
        $Container = "alura-cicd-aula-${Nome}"

        $Existente = @(docker ps -a --format '{{.Names}}')

        if ($Existente -contains $Container) {
            Write-Host "CONTEINER EXISTENTE PRESERVADO: $Container" -ForegroundColor Yellow

            $Ativo = @(docker ps --format '{{.Names}}')

            if ($Ativo -notcontains $Container) {
                docker start $Container

                if ($LASTEXITCODE -ne 0) {
                    $Falhas++
                    continue
                }
            }

            $Mapeamento = @(docker port $Container "$Interna/tcp" 2>$null)

            if ($LASTEXITCODE -eq 0 -and $Mapeamento.Count -gt 0) {
                $Endereco = ($Mapeamento -join " ")

                if ($Endereco -match ':(\d+)$') {
                    $Externa = [int]$Matches[1]
                }
            }
        }
        else {
            docker run -d `
                --name $Container `
                --network $Rede `
                --env-file $ArquivoEnv `
                -p "127.0.0.1:${Externa}:${Interna}" `
                $Imagem

            if ($LASTEXITCODE -ne 0) {
                Write-Host "FALHA AO INICIAR: $Nome" -ForegroundColor Red
                $Falhas++
                continue
            }
        }

        $URL = "http://127.0.0.1:$Externa/"
        $HTTP = "000"

        for ($Tentativa = 1; $Tentativa -le 10; $Tentativa++) {
            $Resposta = & curl.exe -s -o NUL -w '%{http_code}' --max-time 4 $URL

            if ($LASTEXITCODE -eq 0) {
                $HTTP = ([string]$Resposta).Trim()

                if ($HTTP -match '^[23]\d\d$') {
                    break
                }
            }

            Start-Sleep -Seconds 2
        }

        if ($HTTP -match '^[23]\d\d$') {
            Write-Host "OK: $Nome | HTTP $HTTP | $URL" -ForegroundColor Green
        }
        else {
            Write-Host "PENDENTE: $Nome | HTTP $HTTP" -ForegroundColor Yellow
            docker logs --tail 20 $Container
            $Falhas++
        }

        $Resultados += "$Nome | HTTP $HTTP | $URL"
    }

    Write-Host "`n===== 9. IMAGENS DA AULA =====" -ForegroundColor Cyan

    docker images --filter "reference=alura-cicd-*:1.0"

    Write-Host "`n===== 10. CONTEINERES DA AULA =====" -ForegroundColor Cyan

    docker ps -a --filter "name=alura-cicd-aula-" `
        --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

    Write-Host "`n===== 11. RESULTADO FINAL =====" -ForegroundColor Cyan

    $Resultados | ForEach-Object { Write-Host $_ }

    if ($Falhas -eq 0 -and $Resultados.Count -eq 4) {
        Write-Host "`nQUATRO MICROSSERVICOS RESPONDENDO LOCALMENTE." -ForegroundColor Green
    }
    else {
        Write-Host "`nPENDENCIAS IDENTIFICADAS: $Falhas" -ForegroundColor Yellow
    }

    Write-Host "Nenhum commit."
    Write-Host "Nenhum push."
    Write-Host "Nenhuma imagem enviada para registro."
    Write-Host "Nenhum deploy em nuvem."

