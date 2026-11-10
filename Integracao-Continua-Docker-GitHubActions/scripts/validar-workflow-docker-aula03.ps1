& {
    $ErrorActionPreference = "Stop"

    $Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"

    $Arquivo = Join-Path $Projeto "docker-automation\.github\workflows\docker-dev-aula-03.yml"

    if (!(Test-Path $Arquivo -PathType Leaf)) {
        throw "Workflow nao encontrado."
    }

    $Yaml = Get-Content -LiteralPath $Arquivo -Raw

    $Regras = [ordered]@{
        "Nome do workflow" = '(?m)^name: Docker dev workflow - aula 03\s*$'
        "Gatilhos" = '(?m)^on:\s*$'
        "Push" = '(?m)^  push:\s*$'
        "Pull request" = '(?m)^  pull_request:\s*$'
        "Job" = '(?m)^  docker-up:\s*$'
        "Executor Ubuntu" = 'runs-on: ubuntu-latest'
        "Checkout" = 'actions/checkout@v4'
        "Diretorio da aplicacao" = 'working-directory: burguer-app'
        "Compose" = 'docker compose -f docker-compose.yml -f docker-compose.override.yml'
        "Build" = 'up -d --build'
        "MongoDB" = 'Aguardar inicializacao do MongoDB'
        "Teste de conexao" = 'Testar conexao dos microservicos com MongoDB'
        "Teste HTTP" = 'Testar HTTP dos quatro microservicos'
        "Limpeza garantida" = 'if: always\(\)'
    }

    foreach ($Regra in $Regras.GetEnumerator()) {
        if ($Yaml -notmatch $Regra.Value) {
            throw "Verificacao falhou: $($Regra.Key)"
        }

        Write-Host "OK: $($Regra.Key)" -ForegroundColor Green
    }

    $Branches = [regex]::Matches(
        $Yaml,
        '(?m)^      - aula-03\s*$'
    ).Count

    if ($Branches -ne 2) {
        throw "Gatilhos da branch aula-03 incorretos."
    }

    if ($Yaml -match '(?m)^\s*(docker push|docker login|git push)\b') {
        throw "Comando de publicacao inesperado."
    }

    Write-Host "`nESTRUTURA DO WORKFLOW CONFERIDA" -ForegroundColor Green
    Write-Host "Esta verificacao e local; o GitHub Actions ainda nao executou o pipeline."
}
