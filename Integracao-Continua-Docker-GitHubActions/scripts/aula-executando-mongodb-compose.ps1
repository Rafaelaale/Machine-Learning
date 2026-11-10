
        param([string]$Projeto)

        $ErrorActionPreference = "Stop"

        $Aulas = Join-Path $Projeto "aulas"
        $Scripts = Join-Path $Projeto "scripts"

        $Base = Join-Path $Aulas "docker-compose-microservicos-aula.yml"
        $Override = Join-Path $Aulas "docker-compose-mongodb-aula.override.yml"
        $Validador = Join-Path $Scripts "teste-mongodb-compose.py"

        $NomeProjeto = "alura-cicd-compose-aula"
        $Rede = "alura-cicd-aula-rede"

        Set-Location $Projeto

        Write-Host "`n===== 2. VERIFICANDO DOCKER =====" -ForegroundColor Cyan

        docker info --format '{{.ServerVersion}}'

        if ($LASTEXITCODE -ne 0) {
            throw "Docker Engine indisponivel."
        }

        docker compose version

        if ($LASTEXITCODE -ne 0) {
            throw "Docker Compose indisponivel."
        }

        Write-Host "`n===== 3. VALIDANDO COMPOSE =====" -ForegroundColor Cyan

        docker compose -p $NomeProjeto `
            -f $Base `
            -f $Override `
            config --quiet

        if ($LASTEXITCODE -ne 0) {
            throw "Configuracao integrada invalida."
        }

        $Servicos = @(
            docker compose -p $NomeProjeto `
                -f $Base `
                -f $Override `
                config --services
        )

        if ($LASTEXITCODE -ne 0) {
            throw "Falha ao consultar servicos."
        }

        foreach ($Nome in @(
            "mongo",
            "auth-service",
            "user-service",
            "order-service",
            "product-service"
        )) {
            if ($Servicos -notcontains $Nome) {
                throw "Servico ausente: $Nome"
            }

            Write-Host "CONFIGURADO: $Nome" -ForegroundColor Green
        }

        Write-Host "`n===== 4. EXECUTANDO DOCKER COMPOSE =====" -ForegroundColor Cyan

        docker compose -p $NomeProjeto `
            -f $Base `
            -f $Override `
            up -d --build

        if ($LASTEXITCODE -ne 0) {
            throw "Falha no Docker Compose. Verifique os logs acima."
        }

        Write-Host "`n===== 5. VERIFICANDO CINCO CONTEINERES =====" -ForegroundColor Cyan

        docker compose -p $NomeProjeto `
            -f $Base `
            -f $Override `
            ps

        if ($LASTEXITCODE -ne 0) {
            throw "Falha ao consultar os containers."
        }

        Write-Host "`n===== 6. VALIDANDO MONGODB =====" -ForegroundColor Cyan

        $MongoID = @(
            docker compose -p $NomeProjeto `
                -f $Base `
                -f $Override `
                ps -q mongo
        )

        if ($LASTEXITCODE -ne 0 -or !$MongoID) {
            throw "Container MongoDB do Compose nao encontrado."
        }

        $MongoID = $MongoID[0].Trim()

        $Saudavel = $false

        for ($i = 1; $i -le 30; $i++) {
            $Estado = docker inspect $MongoID `
                --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}'

            if ($LASTEXITCODE -eq 0 -and $Estado.Trim() -eq "healthy") {
                $Saudavel = $true
                break
            }

            Start-Sleep -Seconds 3
        }

        if (!$Saudavel) {
            docker logs --tail 40 $MongoID
            throw "MongoDB nao atingiu o estado healthy."
        }

        Write-Host "MONGODB HEALTHY" -ForegroundColor Green

        Write-Host "`n===== 7. VALIDANDO AUTENTICACAO DOS SERVICOS =====" -ForegroundColor Cyan

        $Resultados = @()
        $AprovadosMongo = 0

        foreach ($Nome in @(
            "auth-service",
            "user-service",
            "order-service",
            "product-service"
        )) {
            $ContainerID = @(
                docker compose -p $NomeProjeto `
                    -f $Base `
                    -f $Override `
                    ps -q $Nome
            )

            if ($LASTEXITCODE -ne 0 -or !$ContainerID) {
                $Resultados += "FALHA: $Nome - container ausente"
                continue
            }

            $ContainerID = $ContainerID[0].Trim()

            docker cp $Validador "${ContainerID}:/tmp/teste_mongodb_compose.py"

            if ($LASTEXITCODE -ne 0) {
                $Resultados += "FALHA: $Nome - copia do teste"
                continue
            }

            docker exec $ContainerID python /tmp/teste_mongodb_compose.py

            if ($LASTEXITCODE -eq 0) {
                $AprovadosMongo++
                $Resultados += "APROVADO: $Nome -> MongoDB"
                Write-Host "MONGODB OK: $Nome" -ForegroundColor Green
            }
            else {
                $Resultados += "FALHA: $Nome -> MongoDB"
                Write-Host "MONGODB FALHOU: $Nome" -ForegroundColor Yellow
            }
        }

        Write-Host "`n===== 8. TESTANDO HTTP DOS QUATRO SERVICOS =====" -ForegroundColor Cyan

        $Portas = [ordered]@{
            "auth-service" = 16000
            "user-service" = 16001
            "order-service" = 16002
            "product-service" = 16003
        }

        $AprovadosHTTP = 0

        foreach ($Nome in $Portas.Keys) {
            $Porta = $Portas[$Nome]
            $URL = "http://127.0.0.1:$Porta/"
            $HTTP = "000"

            for ($i = 1; $i -le 12; $i++) {
                $Resposta = & curl.exe `
                    --silent `
                    --location `
                    --output NUL `
                    --write-out '%{http_code}' `
                    --max-time 8 `
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
                $AprovadosHTTP++
                $Resultados += "HTTP 200: $Nome - $URL"
                Write-Host "APROVADO: $Nome - HTTP 200" -ForegroundColor Green
            }
            else {
                $Resultados += "FALHA HTTP: $Nome - $HTTP"
                Write-Host "FALHA: $Nome - HTTP $HTTP" -ForegroundColor Yellow
            }
        }

        Write-Host "`n===== 9. SALVANDO RELATORIO =====" -ForegroundColor Cyan

        $Relatorio = Join-Path $Aulas (
            "resultado-mongodb-compose-" +
            (Get-Date -Format "yyyyMMdd-HHmmss") +
            ".txt"
        )

        @(
            "AULA - EXECUTANDO MONGODB NO DOCKER COMPOSE",
            "",
            "PROJETO: $NomeProjeto",
            "REDE: $Rede",
            "MONGODB HEALTHY: $Saudavel",
            "AUTENTICACAO MONGODB: $AprovadosMongo/4",
            "TESTES HTTP: $AprovadosHTTP/4",
            "",
            $Resultados,
            "",
            "Nenhum commit, push ou deploy em nuvem."
        ) | Set-Content $Relatorio -Encoding UTF8

        Write-Host "RELATORIO: $Relatorio" -ForegroundColor Green

        Write-Host "`n===== RESULTADO FINAL =====" -ForegroundColor Cyan

        $Resultados | ForEach-Object {
            Write-Host $_
        }

        Write-Host "`nMONGODB: $AprovadosMongo/4"
        Write-Host "HTTP: $AprovadosHTTP/4"

        if ($AprovadosMongo -eq 4 -and $AprovadosHTTP -eq 4) {
            Write-Host "`nCINCO SERVICOS INTEGRADOS E VALIDADOS." -ForegroundColor Green
        }
        else {
            Write-Host "`nEXISTEM PENDENCIAS A INVESTIGAR." -ForegroundColor Yellow
        }

        Write-Host "Nenhuma publicacao realizada."
    