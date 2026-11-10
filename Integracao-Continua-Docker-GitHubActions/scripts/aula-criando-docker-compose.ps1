
        param(
            [string]$Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"
        )

        $ErrorActionPreference = "Stop"

        $App = Join-Path $Projeto "docker-automation\burguer-app"
        $Aulas = Join-Path $Projeto "aulas"
        $Compose = Join-Path $Aulas "docker-compose-microservicos-aula.yml"
        $EnvFile = Join-Path $Aulas "microservicos-local.env"
        $Notas = Join-Path $Aulas "aula-criando-docker-compose.txt"
        $Rede = "alura-cicd-aula-rede"
        $Mongo = "alura-cicd-mongodb"
        $NomeProjeto = "alura-cicd-compose-aula"
        $UTF8 = New-Object System.Text.UTF8Encoding($false)

        $Servicos = @(
            @{ Nome = "auth-service"; Interna = 5000; Externa = 16000 },
            @{ Nome = "user-service"; Interna = 5001; Externa = 16001 },
            @{ Nome = "order-service"; Interna = 5002; Externa = 16002 },
            @{ Nome = "product-service"; Interna = 5003; Externa = 16003 }
        )

        Set-Location $Projeto

        Write-Host "`n===== 1. VALIDANDO PROJETO =====" -ForegroundColor Cyan

        docker info --format '{{.ServerVersion}}'
        if ($LASTEXITCODE -ne 0) {
            throw "Docker indisponivel."
        }

        docker compose version
        if ($LASTEXITCODE -ne 0) {
            throw "Docker Compose indisponivel."
        }

        foreach ($Servico in $Servicos) {
            $Pasta = Join-Path $App $Servico.Nome

            foreach ($Nome in @("app.py", "requirements.txt", "Dockerfile")) {
                if (!(Test-Path (Join-Path $Pasta $Nome))) {
                    throw "Arquivo ausente: $Pasta\$Nome"
                }
            }

            $Ignore = Join-Path $Pasta ".dockerignore"

            if (!(Test-Path $Ignore)) {
                throw "Arquivo .dockerignore ausente em $Pasta."
            }

            $Regras = @(Get-Content $Ignore)

            if ($Regras -notcontains ".env") {
                throw "Protecao .env ausente em $Ignore."
            }

            Write-Host "VALIDADO: $($Servico.Nome)" -ForegroundColor Green
        }

        Write-Host "`n===== 2. VERIFICANDO REDE E MONGODB =====" -ForegroundColor Cyan

        $Redes = @(docker network ls --format '{{.Name}}')

        if ($Redes -notcontains $Rede) {
            throw "Rede dedicada nao encontrada."
        }

        $Membros = @(
            docker network inspect $Rede --format '{{range .Containers}}{{println .Name}}{{end}}'
        )

        if ($LASTEXITCODE -ne 0) {
            throw "Falha ao consultar rede."
        }

        if ($Membros -notcontains $Mongo) {
            throw "MongoDB nao esta conectado a rede da aula."
        }

        $Ativos = @(docker ps --format '{{.Names}}')

        if ($Ativos -notcontains $Mongo) {
            throw "MongoDB da trilha nao esta ativo."
        }

        Write-Host "REDE E MONGODB CONFIRMADOS" -ForegroundColor Green

        Write-Host "`n===== 3. VERIFICANDO AMBIENTE LOCAL =====" -ForegroundColor Cyan

        if (!(Test-Path $EnvFile)) {
            $Chave = [guid]::NewGuid().ToString("N")
            $Jwt = [guid]::NewGuid().ToString("N")

            @(
                "MONGO_URI=mongodb://alura-cicd-mongodb:27017/burguer_app_db",
                "SECRET_KEY=$Chave",
                "JWT_SECRET=$Jwt",
                "PYTHONUNBUFFERED=1",
                "PYTHONDONTWRITEBYTECODE=1"
            ) | Set-Content $EnvFile -Encoding UTF8

            Write-Host "AMBIENTE LOCAL CRIADO" -ForegroundColor Green
        }
        else {
            Write-Host "AMBIENTE EXISTENTE PRESERVADO"
        }

        $Variaveis = @(Get-Content $EnvFile)

        if (-not ($Variaveis -match '^MONGO_URI=mongodb://alura-cicd-mongodb:27017')) {
            throw "MONGO_URI local diferente do esperado."
        }

        foreach ($Nome in @("SECRET_KEY", "JWT_SECRET")) {
            if (-not ($Variaveis -match "^$Nome=.+")) {
                throw "Variavel obrigatoria ausente: $Nome"
            }
        }

        Write-Host "`n===== 4. VERIFICANDO PORTAS =====" -ForegroundColor Cyan

        $DoProjeto = @(
            docker ps --filter "label=com.docker.compose.project=$NomeProjeto" --format '{{.Names}}'
        )

        if ($DoProjeto.Count -eq 0) {
            foreach ($Servico in $Servicos) {
                $Porta = $Servico.Externa

                $Ocupada = Get-NetTCPConnection `
                    -LocalPort $Porta `
                    -State Listen `
                    -ErrorAction SilentlyContinue

                if ($Ocupada) {
                    throw "Porta $Porta ocupada. Nenhum conteiner alterado."
                }

                Write-Host "PORTA LIVRE: $Porta" -ForegroundColor Green
            }
        }
        else {
            Write-Host "Containers Compose anteriores detectados. Configuracao preservada."
        }

        Write-Host "`n===== 5. CRIANDO ARQUIVO DOCKER COMPOSE =====" -ForegroundColor Cyan

        $Yaml = @("services:")

        foreach ($Servico in $Servicos) {
            $Nome = $Servico.Nome
            $Interna = $Servico.Interna
            $Externa = $Servico.Externa

            $Yaml += @(
                "  ${Nome}:",
                "    image: alura-cicd-${Nome}:1.0",
                "    build:",
                "      context: ../docker-automation/burguer-app/$Nome",
                "      dockerfile: Dockerfile",
                "    ports:",
                "      - `"127.0.0.1:${Externa}:${Interna}`"",
                "    env_file:",
                "      - ./microservicos-local.env",
                "    networks:",
                "      - alura-cicd-aula-rede"
            )
        }

        $Yaml += @(
            "networks:",
            "  alura-cicd-aula-rede:",
            "    external: true"
        )

        $NovoYaml = ($Yaml -join "`n").Trim() + "`n"

        if (Test-Path $Compose) {
            $Existente = [IO.File]::ReadAllText($Compose)

            if ($Existente.Trim() -ne $NovoYaml.Trim()) {
                throw "Compose existente difere do esperado. Arquivo preservado."
            }

            Write-Host "COMPOSE EXISTENTE PRESERVADO"
        }
        else {
            [IO.File]::WriteAllText($Compose, $NovoYaml, $UTF8)
            Write-Host "COMPOSE CRIADO" -ForegroundColor Green
        }

        Write-Host "`n===== 6. VALIDANDO YAML =====" -ForegroundColor Cyan

        docker compose -p $NomeProjeto -f $Compose config --quiet

        if ($LASTEXITCODE -ne 0) {
            throw "Falha na validacao do YAML."
        }

        $Configurados = @(
            docker compose -p $NomeProjeto -f $Compose config --services
        )

        if ($LASTEXITCODE -ne 0) {
            throw "Falha ao consultar os servicos."
        }

        foreach ($Servico in $Servicos) {
            if ($Configurados -notcontains $Servico.Nome) {
                throw "Servico ausente: $($Servico.Nome)"
            }
        }

        Write-Host "QUATRO SERVICOS CONFIGURADOS" -ForegroundColor Green

        Write-Host "`n===== 7. SALVANDO CODIGOS DA AULA =====" -ForegroundColor Cyan

        $NotasConteudo = @(
            "AULA - CRIANDO O DOCKER COMPOSE",
            "",
            "COMANDOS DO PROFESSOR:",
            "docker ps",
            "docker stop ID_DO_CONTEINER",
            "docker rm ID_DO_CONTEINER",
            "docker-compose up -d --build",
            "",
            "SINTAXE DOCKER COMPOSE ATUAL:",
            "docker compose up -d --build",
            "docker compose ps",
            "docker compose down",
            "",
            "IMPORTANTE:",
            "Nao executar stop, rm ou down em outros projetos.",
            "",
            "COMPOSE DESTA AULA:",
            $Compose,
            "",
            "COMANDO DE EXECUCAO:",
            "docker compose -p $NomeProjeto -f `"$Compose`" up -d --build",
            "",
            "COMANDO DE VERIFICACAO:",
            "docker compose -p $NomeProjeto -f `"$Compose`" ps",
            "",
            "INFRAESTRUTURA:",
            "Rede externa: $Rede",
            "MongoDB: $Mongo",
            "Auth Service: localhost:16000",
            "User Service: localhost:16001",
            "Order Service: localhost:16002",
            "Product Service: localhost:16003",
            "",
            "O arquivo Compose original do professor foi preservado.",
            "Os conteineres anteriores foram preservados.",
            "Nenhum commit, push ou deploy em nuvem."
        )

        if (!(Test-Path $Notas)) {
            $NotasConteudo | Set-Content $Notas -Encoding UTF8
        }

        Write-Host "CODIGOS SALVOS" -ForegroundColor Green

        Write-Host "`n===== 8. CONSTRUINDO E INICIANDO COM COMPOSE =====" -ForegroundColor Cyan

        docker compose -p $NomeProjeto -f $Compose up -d --build --no-recreate

        if ($LASTEXITCODE -ne 0) {
            throw "Falha no Docker Compose up. Consulte a saida do build."
        }

        Write-Host "`n===== 9. VERIFICANDO CONTEINERES =====" -ForegroundColor Cyan

        docker compose -p $NomeProjeto -f $Compose ps

        if ($LASTEXITCODE -ne 0) {
            throw "Falha ao verificar containers."
        }

        Write-Host "`n===== 10. TESTANDO APLICACAO =====" -ForegroundColor Cyan

        $Aprovados = 0

        foreach ($Servico in $Servicos) {
            $URL = "http://127.0.0.1:$($Servico.Externa)/"
            $HTTP = "000"

            for ($Tentativa = 1; $Tentativa -le 15; $Tentativa++) {
                $Resposta = & curl.exe `
                    -L -s -o NUL `
                    -w '%{http_code}' `
                    --max-time 6 `
                    $URL

                if ($LASTEXITCODE -eq 0) {
                    $HTTP = ([string]$Resposta).Trim()

                    if ($HTTP -eq "200") {
                        break
                    }
                }

                Start-Sleep -Seconds 2
            }

            if ($HTTP -eq "200") {
                $Aprovados++
                Write-Host "APROVADO: $($Servico.Nome) | HTTP 200 | $URL" -ForegroundColor Green
            }
            else {
                Write-Host "PENDENTE: $($Servico.Nome) | HTTP $HTTP | $URL" -ForegroundColor Yellow
            }
        }

        Write-Host "`n===== RESULTADO FINAL =====" -ForegroundColor Cyan

        Write-Host "MICROSSERVICOS RESPONDENDO: $Aprovados/4"
        Write-Host "COMPOSE: $Compose"
        Write-Host "REDE: $Rede"
        Write-Host "MongoDB e containers anteriores preservados."
        Write-Host "Nenhum commit."
        Write-Host "Nenhum push."
        Write-Host "Nenhum deploy em nuvem."

        if ($Aprovados -eq 4) {
            Write-Host "DOCKER COMPOSE VALIDADO COM SUCESSO." -ForegroundColor Green
        }
        else {
            Write-Host "HA SERVICOS A INVESTIGAR." -ForegroundColor Yellow
        }

        if (Get-Command code -ErrorAction SilentlyContinue) {
            code -r $Compose $Notas
        }
    