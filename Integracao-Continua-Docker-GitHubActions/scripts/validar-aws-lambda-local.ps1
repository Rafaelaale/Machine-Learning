& {
    $ErrorActionPreference = "Stop"

    $Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"

    $Fonte = Join-Path $Projeto "docker-automation\lambda-estudo\auth-service-lambda"
    $Pasta = Join-Path $Projeto "aulas\aws-lambda"

    $Handler = Join-Path $Fonte "lambda_function.py"
    $Teste = Join-Path $Fonte "teste_lambda_local.py"
    $Workflow = Join-Path $Pasta "Docker-Lambda-rascunho.yml"
    $Zip = Join-Path $Pasta "auth-service-lambda-demo.zip"

    Write-Host "`n===== VALIDANDO ARQUIVOS =====" -ForegroundColor Cyan

    foreach ($Arquivo in @($Handler, $Teste, $Workflow)) {
        if (!(Test-Path $Arquivo -PathType Leaf)) {
            throw "Arquivo ausente: $Arquivo"
        }

        Write-Host "ENCONTRADO: $Arquivo" -ForegroundColor Green
    }

    $Yaml = Get-Content $Workflow -Raw

    foreach ($Termo in @(
        "aula-05",
        'if: ${{ false }}',
        "actions/checkout@v4",
        "python3.12",
        "lambda_function.lambda_handler",
        "auth-service-lambda.zip",
        "aws-actions/configure-aws-credentials@v4",
        "aws lambda update-function-code",
        "aws lambda create-function"
    )) {
        if (!$Yaml.Contains($Termo)) {
            throw "Etapa do workflow ausente: $Termo"
        }

        Write-Host "VALIDADO: $Termo" -ForegroundColor Green
    }

    Write-Host "`n===== EXECUTANDO TESTES PYTHON =====" -ForegroundColor Cyan

    python -B $Teste

    if ($LASTEXITCODE -ne 0) {
        throw "Testes Python falharam."
    }

    Write-Host "`n===== CRIANDO PACOTE ZIP LOCAL =====" -ForegroundColor Cyan

    if (!(Test-Path $Zip -PathType Leaf)) {
        Compress-Archive `
            -LiteralPath $Handler `
            -DestinationPath $Zip `
            -CompressionLevel Optimal `
            -ErrorAction Stop

        Write-Host "PACOTE ZIP CRIADO" -ForegroundColor Green
    }
    else {
        Write-Host "PACOTE ZIP EXISTENTE PRESERVADO"
    }

    Add-Type -AssemblyName System.IO.Compression.FileSystem

    $Pacote = [System.IO.Compression.ZipFile]::OpenRead($Zip)

    try {
        $Entradas = @($Pacote.Entries | ForEach-Object { $_.FullName })

        if ($Entradas -notcontains "lambda_function.py") {
            throw "Handler nao encontrado na raiz do ZIP."
        }

        Write-Host "ZIP VALIDADO: lambda_function.py" -ForegroundColor Green
    }
    finally {
        $Pacote.Dispose()
    }

    Write-Host "`n===== RESULTADO FINAL =====" -ForegroundColor Green

    Write-Host "Funcao Lambda demonstrativa validada."
    Write-Host "Testes locais concluidos."
    Write-Host "Pacote ZIP preparado."
    Write-Host "Workflow de estudo preservado fora da pasta ativa."
    Write-Host "Nenhum codigo publicado."
    Write-Host "Nenhuma funcao AWS criada."
    Write-Host "Nenhum deploy executado."
}
