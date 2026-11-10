& {
    $ErrorActionPreference = "Stop"

    $Arquivo = "F:\Projetos\Docker-GitHubActions-CI-CD\aulas\aws-ecs\docker-ecs-rascunho.yml"

    if (!(Test-Path $Arquivo -PathType Leaf)) {
        throw "Workflow de estudo nao encontrado."
    }

    $Texto = Get-Content -LiteralPath $Arquivo -Raw

    $Termos = @(
        "workflow_dispatch",
        'if: ${{ false }}',
        "actions/checkout@v4",
        "docker/login-action@v3",
        "docker build",
        "docker push",
        "aws-actions/configure-aws-credentials@v4",
        "aws ecs register-task-definition",
        "aws ecs update-service",
        "aws ecs wait services-stable",
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

    if ($Arquivo -match '[\\/]\.github[\\/]workflows[\\/]') {
        throw "O rascunho nao deve ficar na pasta ativa."
    }

    Write-Host "`nESTRUTURA LOCAL CONFERIDA" -ForegroundColor Green
    Write-Host "O deploy permanece desativado."
    Write-Host "Nenhum arquivo ou imagem publicado."
    Write-Host "Nenhuma validacao remota executada."
}
