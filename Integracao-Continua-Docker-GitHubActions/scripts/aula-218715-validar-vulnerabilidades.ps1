& {
    $ErrorActionPreference = "Stop"

    $Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"
    $Repositorio = Join-Path $Projeto "docker-automation"

    $Notas = Join-Path $Projeto "aulas\seguranca-pipelines\aula-218715-ferramentas-vulnerabilidades.txt"

    Write-Host "`n===== VALIDANDO CONCEITOS =====" -ForegroundColor Cyan

    if (!(Test-Path -LiteralPath $Notas -PathType Leaf)) {
        throw "Anotacoes da aula nao encontradas."
    }

    $Texto = [IO.File]::ReadAllText($Notas)

    $Conceitos = @(
        "CVE",
        "CVSS",
        "TRIVY",
        "SNYK",
        "RED HAT QUAY",
        "OPENSSL",
        "DOCKER",
        "GITHUB ACTIONS",
        "VULNERABILIDADES",
        "DEPENDENCIAS",
        "IMAGENS",
        "SEGURANCA"
    )

    foreach ($Conceito in $Conceitos) {

        if ($Texto.IndexOf(
                $Conceito,
                [StringComparison]::OrdinalIgnoreCase
            ) -lt 0) {
            throw "Conceito ausente: $Conceito"
        }

        Write-Host "VALIDADO: $Conceito" -ForegroundColor Green
    }

    Write-Host "`n===== INVENTARIO DE DOCKERFILES =====" -ForegroundColor Cyan

    $Servicos = @(
        "auth-service",
        "user-service",
        "order-service",
        "product-service"
    )

    $Total = 0

    foreach ($Servico in $Servicos) {

        $Dockerfile = Join-Path $Repositorio "burguer-app\$Servico\Dockerfile"

        if (!(Test-Path -LiteralPath $Dockerfile -PathType Leaf)) {
            throw "Dockerfile nao encontrado: $Servico"
        }

        $Linhas = Get-Content -LiteralPath $Dockerfile

        $ImagensBase = @(
            $Linhas | Where-Object {
                $_ -match '^\s*FROM\s+'
            }
        )

        if ($ImagensBase.Count -eq 0) {
            throw "Imagem base nao identificada: $Servico"
        }

        Write-Host "DOCKERFILE IDENTIFICADO: $Servico" -ForegroundColor Green

        foreach ($Linha in $ImagensBase) {
            Write-Host "IMAGEM BASE: $($Linha.Trim())"
        }

        $Total++
    }

    Write-Host "`n===== CONFERINDO SEGURANCA DO REPOSITORIO =====" -ForegroundColor Cyan

    if (Get-Command git -ErrorAction SilentlyContinue) {

        $Rastreado = @(
            git -C $Repositorio ls-files -- "burguer-app/auth-service/.env"
        )

        if ($LASTEXITCODE -ne 0) {
            throw "Falha ao consultar o indice Git."
        }

        if ($Rastreado.Count -gt 0) {
            Write-Host "ALERTA: auth-service/.env rastreado pelo Git." -ForegroundColor Yellow
            Write-Host "Correcao obrigatoria antes da publicacao." -ForegroundColor Yellow
        }
        else {
            Write-Host "auth-service/.env nao aparece no indice Git." -ForegroundColor Green
        }
    }
    else {
        Write-Host "Git nao disponivel. Auditoria pendente." -ForegroundColor Yellow
    }

    Write-Host "`n===== RESULTADO FINAL =====" -ForegroundColor Green

    Write-Host "CONCEITOS VALIDADOS: $($Conceitos.Count)"
    Write-Host "DOCKERFILES IDENTIFICADOS: $Total/4"
    Write-Host "Inventario local concluido."
    Write-Host "Nenhuma vulnerabilidade foi pesquisada."
    Write-Host "Nenhuma imagem Docker modificada."
    Write-Host "Nenhum scanner instalado."
    Write-Host "Nenhum codigo publicado."
    Write-Host "Nenhum commit, push ou deploy."
}
