& {
    $ErrorActionPreference = "Stop"

    $Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"

    $Pasta = Join-Path $Projeto "aulas\versionamento"

    $Manifesto = Join-Path $Pasta "releases-rollback-exemplo.json"
    $Workflow = Join-Path $Pasta "docker-rollback-rascunho.yml"
    $Notas = Join-Path $Pasta "aula-218719-estrategia-rollback.txt"

    $Relatorio = Join-Path $Projeto "relatorios\versionamento\aula-218719-rollback-simulacao.txt"

    Write-Host "`n===== VALIDANDO ARQUIVOS =====" -ForegroundColor Cyan

    foreach ($Arquivo in @($Manifesto, $Workflow, $Notas)) {
        if (!(Test-Path $Arquivo -PathType Leaf)) {
            throw "Arquivo ausente: $Arquivo"
        }

        Write-Host "ENCONTRADO: $([IO.Path]::GetFileName($Arquivo))" -ForegroundColor Green
    }

    Write-Host "`n===== VALIDANDO MANIFESTO =====" -ForegroundColor Cyan

    $Dados = Get-Content -LiteralPath $Manifesto -Raw |
        ConvertFrom-Json

    if ($Dados.ambiente -ne "SIMULACAO_LOCAL") {
        throw "Manifesto nao identificado como simulacao."
    }

    if ($Dados.executar_rollback -ne $false) {
        throw "Execucao real nao autorizada."
    }

    $Atual = [string]$Dados.versao_atual
    $Anterior = [string]$Dados.versao_anterior

    if ($Atual -cnotmatch '^[a-f0-9]{7,40}$') {
        throw "Versao atual invalida."
    }

    if ($Anterior -cnotmatch '^[a-f0-9]{7,40}$') {
        throw "Versao anterior invalida."
    }

    if ($Atual -ceq $Anterior) {
        throw "Versoes iguais. Rollback invalido."
    }

    Write-Host "VERSAO ATUAL SIMULADA: $Atual" -ForegroundColor Green
    Write-Host "VERSAO ANTERIOR SIMULADA: $Anterior" -ForegroundColor Green

    Write-Host "`n===== VALIDANDO SERVICOS =====" -ForegroundColor Cyan

    $Esperados = @(
        "auth-service",
        "user-service",
        "order-service",
        "product-service"
    )

    $Servicos = @($Dados.servicos)

    if ($Servicos.Count -ne 4) {
        throw "Quantidade de servicos incorreta."
    }

    foreach ($Servico in $Esperados) {
        if ($Servicos -notcontains $Servico) {
            throw "Servico ausente: $Servico"
        }
    }

    $Plano = New-Object System.Collections.Generic.List[string]

    $Plano.Add("AULA 218719 - SIMULACAO DE ROLLBACK")
    $Plano.Add("VERSAO ATUAL: $Atual")
    $Plano.Add("VERSAO ANTERIOR: $Anterior")
    $Plano.Add("")

    foreach ($Servico in $Esperados) {
        $ImagemAtual = "burguer-app-${Servico}:${Atual}"
        $ImagemAnterior = "burguer-app-${Servico}:${Anterior}"

        Write-Host "SERVICO: $Servico" -ForegroundColor Cyan
        Write-Host "ATUAL: $ImagemAtual"
        Write-Host "ROLLBACK PLANEJADO: $ImagemAnterior" -ForegroundColor Green

        $Plano.Add("$Servico")
        $Plano.Add("ATUAL: $ImagemAtual")
        $Plano.Add("ANTERIOR: $ImagemAnterior")
        $Plano.Add("")
    }

    Write-Host "`n===== VALIDANDO WORKFLOW =====" -ForegroundColor Cyan

    $Texto = [IO.File]::ReadAllText($Workflow)

    $Termos = @(
        'if: ${{ false }}',
        "workflow_dispatch",
        "runs-on: self-hosted",
        "previous_sha",
        "current_sha",
        "actions/checkout@v4",
        "docker image inspect",
        "docker compose",
        "config --quiet",
        "up -d --no-build --no-deps",
        "auth-service",
        "user-service",
        "order-service",
        "product-service"
    )

    foreach ($Termo in $Termos) {
        if (!$Texto.Contains($Termo)) {
            throw "Configuracao ausente: $Termo"
        }

        Write-Host "VALIDADO: $Termo" -ForegroundColor Green
    }

    if ($Texto.Contains("down --volumes")) {
        throw "Operacao de remocao de volumes identificada."
    }

    if ($Texto.Contains("docker rmi")) {
        throw "Remocao de imagens identificada."
    }

    if ($Workflow -match '[\\/]\.github[\\/]workflows[\\/]') {
        throw "Rascunho localizado em pasta ativa."
    }

    Write-Host "`n===== SALVANDO RELATORIO =====" -ForegroundColor Cyan

    $Plano.Add("SERVICOS CONFERIDOS: 4/4")
    $Plano.Add("WORKFLOW DESATIVADO")
    $Plano.Add("NENHUM ROLLBACK REAL EXECUTADO")
    $Plano.Add("NENHUM CONTAINER ALTERADO")
    $Plano.Add("NENHUM CODIGO PUBLICADO")

    if (!(Test-Path $Relatorio -PathType Leaf)) {
        [IO.File]::WriteAllLines(
            $Relatorio,
            [string[]]$Plano.ToArray(),
            (New-Object System.Text.UTF8Encoding($false))
        )
    }

    Write-Host "`n===== RESULTADO FINAL =====" -ForegroundColor Green

    Write-Host "VERSOES CONFERIDAS: 2/2"
    Write-Host "SERVICOS CONFERIDOS: 4/4"
    Write-Host "ETAPAS DO WORKFLOW: $($Termos.Count)"
    Write-Host "SIMULACAO DE ROLLBACK APROVADA."
    Write-Host "Relatorio: $Relatorio"
    Write-Host "Nenhum Docker executado."
    Write-Host "Nenhum container ou volume modificado."
    Write-Host "Nenhum rollback real executado."
    Write-Host "Nenhum codigo publicado."
}
