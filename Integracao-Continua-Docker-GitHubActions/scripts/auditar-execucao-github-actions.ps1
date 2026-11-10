& {
    $ErrorActionPreference = "Stop"

    $Repositorio = "F:\Projetos\Docker-GitHubActions-CI-CD\docker-automation"
    $Workflow = Join-Path $Repositorio ".github\workflows\docker-dev-aula-03.yml"

    Set-Location $Repositorio

    Write-Host "`n===== 1. VERIFICANDO GIT =====" -ForegroundColor Cyan

    git --version

    if ($LASTEXITCODE -ne 0) {
        throw "Git indisponivel."
    }

    git rev-parse --show-toplevel

    if ($LASTEXITCODE -ne 0) {
        throw "Diretorio nao e um repositorio Git."
    }

    Write-Host "`n===== 2. VERIFICANDO WORKFLOW =====" -ForegroundColor Cyan

    $Texto = Get-Content -LiteralPath $Workflow -Raw

    $Regras = [ordered]@{
        "Gatilho GitHub Actions" = '(?m)^on:\s*$'
        "Push" = '(?m)^  push:\s*$'
        "Pull request" = '(?m)^  pull_request:\s*$'
        "Branch aula-03" = 'aula-03'
        "Checkout" = 'actions/checkout@v4'
        "Diretorio correto" = 'working-directory: burguer-app'
        "Docker Compose" = 'docker compose -f docker-compose.yml'
        "Subir containers" = 'up -d --build'
        "Verificar MongoDB" = 'Aguardar inicializacao do MongoDB'
        "Testar HTTP" = 'Testar HTTP dos quatro microservicos'
        "Encerramento" = 'if: always\(\)'
    }

    foreach ($Regra in $Regras.GetEnumerator()) {
        if ($Texto -notmatch $Regra.Value) {
            throw "Configuracao ausente: $($Regra.Key)"
        }

        Write-Host "OK: $($Regra.Key)" -ForegroundColor Green
    }

    Write-Host "`n===== 3. VERIFICANDO BRANCH =====" -ForegroundColor Cyan

    $Branch = (& git branch --show-current).Trim()

    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao consultar branch."
    }

    Write-Host "BRANCH ATUAL: $Branch"

    $BranchAula = @(git branch --list "aula-03")

    if ($BranchAula.Count -gt 0) {
        Write-Host "BRANCH aula-03 JA EXISTE LOCALMENTE" -ForegroundColor Green
    }
    else {
        Write-Host "BRANCH aula-03 AINDA NAO EXISTE LOCALMENTE" -ForegroundColor Yellow
    }

    Write-Host "`n===== 4. VERIFICANDO REPOSITORIO REMOTO =====" -ForegroundColor Cyan

    $Origin = & git remote get-url origin

    if ($LASTEXITCODE -ne 0) {
        Write-Host "REMOTE ORIGIN NAO CONFIGURADO" -ForegroundColor Yellow
    }
    else {
        Write-Host "ORIGIN: $Origin"

        if ($Origin -match 'Danilo-Miguel/docker-automation') {
            Write-Host "ATENCAO: origin aponta para o repositorio do professor." -ForegroundColor Yellow
            Write-Host "Confirmar repositorio proprio antes de qualquer push." -ForegroundColor Yellow
        }
    }

    Write-Host "`n===== 5. VERIFICANDO ALTERACOES =====" -ForegroundColor Cyan

    git status --short --branch

    if ($LASTEXITCODE -ne 0) {
        throw "Falha no git status."
    }

    Write-Host "`n===== 6. AUDITANDO ARQUIVOS DE AMBIENTE =====" -ForegroundColor Cyan

    $Ambientes = @(
        "burguer-app/.env",
        "burguer-app/auth-service/.env",
        "burguer-app/user-service/.env",
        "burguer-app/order-service/.env",
        "burguer-app/product-service/.env"
    )

    $Riscos = @()

    foreach ($Relativo in $Ambientes) {
        $Caminho = Join-Path $Repositorio $Relativo

        if (!(Test-Path $Caminho)) {
            Write-Host "AUSENTE: $Relativo"
            continue
        }

        $Rastreado = @(git ls-files --cached -- $Relativo)

        if ($Rastreado.Count -gt 0) {
            $Riscos += $Relativo
            Write-Host "ATENCAO - ARQUIVO RASTREADO: $Relativo" -ForegroundColor Yellow
        }
        else {
            git check-ignore -q -- $Relativo

            if ($LASTEXITCODE -eq 0) {
                Write-Host "IGNORADO PELO GIT: $Relativo" -ForegroundColor Green
            }
            else {
                $Riscos += $Relativo
                Write-Host "ATENCAO - ARQUIVO NAO IGNORADO: $Relativo" -ForegroundColor Yellow
            }
        }
    }

    Write-Host "`n===== 7. RESULTADO DA AUDITORIA =====" -ForegroundColor Cyan

    Write-Host "Workflow analisado."
    Write-Host "Branch atual: $Branch"
    Write-Host "Arquivos .env com risco de publicacao: $($Riscos.Count)"

    if ($Riscos.Count -gt 0) {
        Write-Host "CORRIGIR PROTECAO DOS ARQUIVOS ANTES DE PUBLICAR." -ForegroundColor Yellow
    }

    Write-Host "NENHUM GIT ADD EXECUTADO."
    Write-Host "NENHUM COMMIT EXECUTADO."
    Write-Host "NENHUM PUSH EXECUTADO."
    Write-Host "NENHUM CONTAINER ALTERADO."
}
