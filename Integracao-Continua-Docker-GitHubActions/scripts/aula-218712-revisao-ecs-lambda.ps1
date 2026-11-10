& {
    $ErrorActionPreference = "Stop"

    $Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"

    $Python = Join-Path $Projeto "scripts\validar-revisao-ecs-lambda.py"

    $Teste = Join-Path $Projeto "docker-automation\lambda-estudo\auth-service-lambda\teste_lambda_local.py"

    $LambdaYaml = Join-Path $Projeto "aulas\aws-lambda\Docker-Lambda-rascunho.yml"

    $EcsYaml = Join-Path $Projeto "aulas\aws-ecs\docker-ecs-rascunho.yml"

    Set-Location $Projeto

    Write-Host "`n===== 1. VALIDANDO CODIGO ORIGINAL =====" -ForegroundColor Cyan

    python -B $Python

    if ($LASTEXITCODE -ne 0) {
        throw "Falha na revisao estatica Python."
    }

    Write-Host "`n===== 2. TESTANDO LAMBDA DEMONSTRATIVA =====" -ForegroundColor Cyan

    python -B $Teste

    if ($LASTEXITCODE -ne 0) {
        throw "Testes da Lambda demonstrativa falharam."
    }

    Write-Host "`n===== 3. CONFERINDO WORKFLOWS DESATIVADOS =====" -ForegroundColor Cyan

    foreach ($Arquivo in @($LambdaYaml, $EcsYaml)) {
        if (!(Test-Path $Arquivo -PathType Leaf)) {
            throw "Workflow de estudo ausente: $Arquivo"
        }

        $Texto = [IO.File]::ReadAllText($Arquivo)

        if (!$Texto.Contains('if: ${{ false }}')) {
            throw "Job nao esta desativado: $Arquivo"
        }

        if ($Arquivo -match '[\\/]\.github[\\/]workflows[\\/]') {
            throw "Workflow em pasta ativa: $Arquivo"
        }

        Write-Host "RASCUNHO DESATIVADO: $([IO.Path]::GetFileName($Arquivo))" -ForegroundColor Green
    }

    Write-Host "`n===== RESULTADO FINAL =====" -ForegroundColor Green

    Write-Host "Codigo Flask analisado sem executar o servidor."
    Write-Host "Serializacao de usuarios conferida."
    Write-Host "Lambda demonstrativa testada."
    Write-Host "Pacote ZIP conferido."
    Write-Host "Rascunhos ECS e Lambda desativados."
    Write-Host "Nenhum codigo publicado."
    Write-Host "Nenhum container modificado."
    Write-Host "Nenhum deploy executado."
}
