& {
    $ErrorActionPreference = "Stop"

    $Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"

    $Arquivo = Join-Path $Projeto "aulas\aws-ecs\microservice-task.exemplo.json"

    if (!(Test-Path $Arquivo -PathType Leaf)) {
        throw "Task Definition nao encontrada."
    }

    $Task = Get-Content -LiteralPath $Arquivo -Raw |
        ConvertFrom-Json

    Write-Host "`n===== VALIDANDO TASK DEFINITION =====" -ForegroundColor Cyan

    if ($Task.family -ne "microservice-task") {
        throw "Nome da Task Definition incorreto."
    }

    if ($Task.networkMode -ne "awsvpc") {
        throw "Network mode incorreto."
    }

    if (@($Task.requiresCompatibilities) -notcontains "FARGATE") {
        throw "Compatibilidade Fargate ausente."
    }

    if (@($Task.containerDefinitions).Count -ne 4) {
        throw "A Task deve conter quatro containers."
    }

    $Esperados = [ordered]@{
        "auth-service" = 5000
        "user-service" = 5001
        "order-service" = 5002
        "product-service" = 5003
    }

    foreach ($Nome in $Esperados.Keys) {
        $Encontrados = @(
            $Task.containerDefinitions |
                Where-Object { $_.name -eq $Nome }
        )

        if ($Encontrados.Count -ne 1) {
            throw "Container ausente ou duplicado: $Nome"
        }

        $Container = $Encontrados[0]
        $Porta = [int]$Esperados[$Nome]

        if (@($Container.portMappings).Count -ne 1) {
            throw "Mapeamento de portas inesperado: $Nome"
        }

        if ([int]$Container.portMappings[0].containerPort -ne $Porta) {
            throw "Porta incorreta: $Nome"
        }

        if (!$Container.image.StartsWith("docker.io/professordanilo/")) {
            throw "Imagem de referencia diferente: $Nome"
        }

        Write-Host "VALIDADO: $Nome | PORTA $Porta" -ForegroundColor Green
    }

    Write-Host "`n===== RESULTADO FINAL =====" -ForegroundColor Green

    Write-Host "TASK FAMILY: $($Task.family)"
    Write-Host "REDE: $($Task.networkMode)"
    Write-Host "CPU: $($Task.cpu)"
    Write-Host "MEMORIA: $($Task.memory)"
    Write-Host "CONTAINERS VALIDADOS: 4/4"

    Write-Host "DEFINICAO JSON VALIDADA LOCALMENTE."
    Write-Host "A configuracao ainda nao foi validada pela AWS."
    Write-Host "Nenhum recurso AWS criado."
    Write-Host "Nenhum deploy ou publicacao."
}
