
    param([string]$Projeto)

    $ErrorActionPreference = "Stop"
    $Rede = "alura-cicd-aula-rede"
    $PythonFile = Join-Path $Projeto "scripts\validar-rede-interna.py"
    $Aulas = Join-Path $Projeto "aulas"

    Set-Location $Projeto

    Write-Host "`n===== 1. VERIFICANDO DOCKER =====" -ForegroundColor Cyan

    docker info --format '{{.ServerVersion}}'

    if ($LASTEXITCODE -ne 0) {
        throw "Docker indisponivel."
    }

    Write-Host "`n===== 2. VERIFICANDO REDE =====" -ForegroundColor Cyan

    $Redes = @(docker network ls --format '{{.Name}}')

    if ($Redes -notcontains $Rede) {
        throw "Rede da aula nao encontrada: $Rede"
    }

    $Containers = @(
        "alura-cicd-mongodb",
        "alura-cicd-aula-auth-service",
        "alura-cicd-aula-user-service",
        "alura-cicd-aula-order-service",
        "alura-cicd-aula-product-service"
    )

    $Membros = @(
        docker network inspect $Rede `
            --format '{{range .Containers}}{{println .Name}}{{end}}'
    )

    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao inspecionar rede."
    }

    $Ativos = @(docker ps --format '{{.Names}}')

    foreach ($Nome in $Containers) {
        if ($Ativos -notcontains $Nome) {
            throw "Conteiner nao esta ativo: $Nome"
        }

        if ($Membros -notcontains $Nome) {
            throw "Conteiner fora da rede: $Nome"
        }

        Write-Host "OK NA REDE: $Nome" -ForegroundColor Green
    }

    Write-Host "`n===== 3. TESTANDO COMUNICACAO REAL =====" -ForegroundColor Cyan

    $Testes = @(
        @{
            Origem = "alura-cicd-aula-auth-service"
            Modo = "http"
            Destino = "http://alura-cicd-aula-user-service:5001/user/create"
        },
        @{
            Origem = "alura-cicd-aula-user-service"
            Modo = "http"
            Destino = "http://alura-cicd-aula-auth-service:5000/auth/login"
        },
        @{
            Origem = "alura-cicd-aula-order-service"
            Modo = "http"
            Destino = "http://alura-cicd-aula-product-service:5003/product/api/products"
        },
        @{
            Origem = "alura-cicd-aula-user-service"
            Modo = "mongo"
            Destino = ""
        }
    )

    $Resultados = @()
    $Aprovados = 0

    foreach ($Teste in $Testes) {
        $Origem = $Teste.Origem
        $Modo = $Teste.Modo

        Write-Host "`nORIGEM: $Origem | TESTE: $Modo" -ForegroundColor Yellow

        docker cp $PythonFile "${Origem}:/tmp/alura_validar_rede.py"

        if ($LASTEXITCODE -ne 0) {
            throw "Falha ao copiar validador para $Origem"
        }

        if ($Modo -eq "http") {
            docker exec $Origem python `
                /tmp/alura_validar_rede.py http $Teste.Destino
        }
        else {
            docker exec $Origem python `
                /tmp/alura_validar_rede.py mongo
        }

        if ($LASTEXITCODE -eq 0) {
            $Aprovados++
            $Resultados += "APROVADO: $Origem - $Modo"
            Write-Host "TESTE APROVADO" -ForegroundColor Green
        }
        else {
            $Resultados += "FALHOU: $Origem - $Modo"
            Write-Host "TESTE FALHOU" -ForegroundColor Red
        }
    }

    Write-Host "`n===== 4. RESULTADO FINAL =====" -ForegroundColor Cyan

    $Resultados | ForEach-Object {
        Write-Host $_
    }

    $Relatorio = Join-Path $Aulas (
        "resultado-rede-corrigido-" +
        (Get-Date -Format "yyyyMMdd-HHmmss") +
        ".txt"
    )

    @(
        "AULA - REDE DEDICADA DOCKER",
        "REDE: $Rede",
        "APROVADOS: $Aprovados/4",
        "",
        $Resultados,
        "",
        "Nenhum commit, push ou deploy."
    ) | Set-Content $Relatorio -Encoding UTF8

    Write-Host "`nAPROVADOS: $Aprovados/4"
    Write-Host "RELATORIO: $Relatorio"
    Write-Host "Nenhum container parado ou removido."
    Write-Host "Nenhuma publicacao realizada."

    if ($Aprovados -eq 4) {
        Write-Host "REDE DEDICADA VALIDADA." -ForegroundColor Green
    }
    else {
        Write-Host "EXISTEM FALHAS REAIS A INVESTIGAR." -ForegroundColor Yellow
    }
