
    param([string]$Projeto)

    $ErrorActionPreference = "Stop"
    $Rede = "alura-cicd-aula-rede"

    $Containers = @(
        "alura-cicd-mongodb",
        "alura-cicd-aula-auth-service",
        "alura-cicd-aula-user-service",
        "alura-cicd-aula-order-service",
        "alura-cicd-aula-product-service"
    )

    Set-Location $Projeto

    Write-Host "`n===== 1. VALIDANDO DOCKER =====" -ForegroundColor Cyan

    docker info --format '{{.ServerVersion}}'

    if ($LASTEXITCODE -ne 0) {
        throw "Docker indisponivel."
    }

    Write-Host "`n===== 2. VERIFICANDO REDE DEDICADA =====" -ForegroundColor Cyan

    $Redes = @(docker network ls --format '{{.Name}}')

    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao consultar redes."
    }

    if ($Redes -notcontains $Rede) {
        docker network create $Rede

        if ($LASTEXITCODE -ne 0) {
            throw "Falha ao criar rede."
        }

        Write-Host "REDE CRIADA: $Rede" -ForegroundColor Green
    }
    else {
        Write-Host "REDE EXISTENTE REUTILIZADA: $Rede" -ForegroundColor Green
    }

    Write-Host "`n===== 3. VALIDANDO CONTEINERES =====" -ForegroundColor Cyan

    $Ativos = @(docker ps --format '{{.Names}}')

    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao listar conteineres."
    }

    foreach ($Nome in $Containers) {
        if ($Ativos -notcontains $Nome) {
            throw "Conteiner nao esta ativo: $Nome"
        }

        $JSON = docker inspect $Nome --format '{{json .NetworkSettings.Networks}}'

        if ($LASTEXITCODE -ne 0) {
            throw "Falha ao inspecionar: $Nome"
        }

        $RedesContainer = $JSON | ConvertFrom-Json

        if ($RedesContainer.PSObject.Properties.Name -notcontains $Rede) {
            docker network connect $Rede $Nome

            if ($LASTEXITCODE -ne 0) {
                throw "Falha ao conectar $Nome a rede."
            }

            Write-Host "CONECTADO: $Nome" -ForegroundColor Green
        }
        else {
            Write-Host "JA CONECTADO: $Nome" -ForegroundColor Green
        }
    }

    Write-Host "`n===== 4. VERIFICANDO MEMBROS DA REDE =====" -ForegroundColor Cyan

    docker network inspect $Rede --format '{{range .Containers}}{{println .Name}}{{end}}'

    if ($LASTEXITCODE -ne 0) {
        throw "Falha na inspecao da rede."
    }

    Write-Host "`n===== 5. TESTANDO COMUNICACAO HTTP INTERNA =====" -ForegroundColor Cyan

    $Testes = @(
        @{
            Origem = "alura-cicd-aula-auth-service"
            Destino = "alura-cicd-aula-user-service"
            Porta = 5001
            Caminho = "/user/create"
        },
        @{
            Origem = "alura-cicd-aula-user-service"
            Destino = "alura-cicd-aula-auth-service"
            Porta = 5000
            Caminho = "/auth/login"
        },
        @{
            Origem = "alura-cicd-aula-order-service"
            Destino = "alura-cicd-aula-product-service"
            Porta = 5003
            Caminho = "/product/api/products"
        }
    )

    $PythonHTTP = 'import sys,urllib.request; u=sys.argv[1]; r=urllib.request.urlopen(u,timeout=10); print("HTTP",r.status,u); sys.exit(0 if r.status==200 else 1)'

    $Falhas = 0
    $Resultados = @()

    foreach ($Teste in $Testes) {
        $URL = "http://$($Teste.Destino):$($Teste.Porta)$($Teste.Caminho)"

        Write-Host "`nTESTANDO: $($Teste.Origem) -> $($Teste.Destino)"

        docker exec $Teste.Origem python -c $PythonHTTP $URL

        if ($LASTEXITCODE -eq 0) {
            Write-Host "COMUNICACAO APROVADA" -ForegroundColor Green
            $Resultados += "OK: $($Teste.Origem) -> $($Teste.Destino)"
        }
        else {
            Write-Host "COMUNICACAO FALHOU" -ForegroundColor Yellow
            $Resultados += "FALHA: $($Teste.Origem) -> $($Teste.Destino)"
            $Falhas++
        }
    }

    Write-Host "`n===== 6. TESTANDO CONEXAO COM MONGODB =====" -ForegroundColor Cyan

    $PythonMongo = 'import os,pymongo; c=pymongo.MongoClient(os.environ["MONGO_URI"],serverSelectionTimeoutMS=5000); print("MONGODB PING:",c.admin.command("ping")["ok"])'

    docker exec alura-cicd-aula-user-service python -c $PythonMongo

    if ($LASTEXITCODE -eq 0) {
        Write-Host "MONGODB ACESSIVEL PELO MICROSSERVICO" -ForegroundColor Green
        $Resultados += "OK: user-service -> MongoDB"
    }
    else {
        Write-Host "FALHA NA CONEXAO COM MONGODB" -ForegroundColor Yellow
        $Resultados += "FALHA: user-service -> MongoDB"
        $Falhas++
    }

    Write-Host "`n===== 7. RESUMO =====" -ForegroundColor Cyan

    $Resultados | ForEach-Object { Write-Host $_ }

    if ($Falhas -eq 0) {
        Write-Host "`nREDE DEDICADA VALIDADA COM SUCESSO." -ForegroundColor Green
    }
    else {
        Write-Host "`nFALHAS ENCONTRADAS: $Falhas" -ForegroundColor Yellow
    }

    Write-Host "Nenhum conteiner removido."
    Write-Host "Nenhum commit, push ou deploy realizado."

    return $Resultados

