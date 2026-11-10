& {
    $ErrorActionPreference = "Stop"

    $Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"

    $PastaTrivy = Join-Path $Projeto "ferramentas\trivy-0.76.2"
    $Relatorios = Join-Path $Projeto "relatorios\trivy"

    New-Item -ItemType Directory -Force -Path `
        $PastaTrivy, $Relatorios | Out-Null

    Set-Location $Projeto

    Write-Host "`n===== 1. VERIFICANDO TRIVY =====" -ForegroundColor Cyan

    $Trivy = Join-Path $PastaTrivy "trivy.exe"

    if (!(Test-Path $Trivy -PathType Leaf)) {

        $Instalado = Get-Command trivy -ErrorAction SilentlyContinue

        if ($Instalado) {
            $Trivy = $Instalado.Source
            Write-Host "TRIVY JA INSTALADO" -ForegroundColor Green
        }
        else {
            Write-Host "PREPARANDO TRIVY PORTATIL PARA WINDOWS" -ForegroundColor Cyan

            $Versao = "0.76.2"

            $Pacote = "trivy_0.76.2_windows-64bit.zip"
            $ChecksumNome = "trivy_${Versao}_checksums.txt"

            $BaseURL = "https://github.com/aquasecurity/trivy/releases/download/v$Versao"

            $ArquivoZip = Join-Path $PastaTrivy $Pacote
            $ArquivoChecksum = Join-Path $PastaTrivy $ChecksumNome

            [Net.ServicePointManager]::SecurityProtocol = `
                [Net.ServicePointManager]::SecurityProtocol -bor `
                [Net.SecurityProtocolType]::Tls12

            Write-Host "BAIXANDO PACOTE OFICIAL..." -ForegroundColor Cyan

            Invoke-WebRequest `
                -Uri "$BaseURL/$Pacote" `
                -OutFile $ArquivoZip `
                -UseBasicParsing

            Write-Host "BAIXANDO CHECKSUM OFICIAL..." -ForegroundColor Cyan

            Invoke-WebRequest `
                -Uri "$BaseURL/$ChecksumNome" `
                -OutFile $ArquivoChecksum `
                -UseBasicParsing

            Write-Host "`n===== 2. VALIDANDO SHA256 =====" -ForegroundColor Cyan

            $Linhas = Get-Content -LiteralPath $ArquivoChecksum

            $Esperado = $null

            foreach ($Linha in $Linhas) {

                if ($Linha -match '^\s*([0-9a-fA-F]{64})\s+\*?trivy_0\.76\.2_windows-64bit\.zip\s*$') {
                    $Esperado = $Matches[1].ToUpperInvariant()
                    break
                }
            }

            if (!$Esperado) {
                throw "Checksum oficial nao encontrado. Instalacao interrompida."
            }

            $Encontrado = (Get-FileHash `
                -LiteralPath $ArquivoZip `
                -Algorithm SHA256).Hash.ToUpperInvariant()

            if ($Encontrado -cne $Esperado) {
                throw "SHA256 invalido. Pacote nao sera executado."
            }

            Write-Host "SHA256 VALIDADO" -ForegroundColor Green

            Write-Host "`n===== 3. EXTRAINDO TRIVY =====" -ForegroundColor Cyan

            Expand-Archive `
                -LiteralPath $ArquivoZip `
                -DestinationPath $PastaTrivy `
                -Force

            $Trivy = Join-Path $PastaTrivy "trivy.exe"

            if (!(Test-Path $Trivy -PathType Leaf)) {
                throw "Executavel Trivy nao encontrado apos extracao."
            }

            Write-Host "TRIVY INSTALADO LOCALMENTE" -ForegroundColor Green
        }
    }
    else {
        Write-Host "TRIVY PORTATIL JA EXISTE" -ForegroundColor Green
    }

    & $Trivy --version

    if ($LASTEXITCODE -ne 0) {
        throw "Falha ao executar o Trivy."
    }

    Write-Host "`n===== 4. VERIFICANDO DOCKER =====" -ForegroundColor Cyan

    if (!(Get-Command docker -ErrorAction SilentlyContinue)) {
        throw "Docker nao encontrado."
    }

    $ImagensLocais = @(
        docker image ls --format "{{.Repository}}:{{.Tag}}"
    )

    if ($LASTEXITCODE -ne 0) {
        throw "Nao foi possivel consultar as imagens Docker."
    }

    $Servicos = @(
        "auth-service",
        "user-service",
        "order-service",
        "product-service"
    )

    $Resumo = New-Object System.Collections.Generic.List[string]

    $Resumo.Add("AULA 218716 - RELATORIO CONSOLIDADO TRIVY")
    $Resumo.Add("Data: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
    $Resumo.Add("Projeto: $Projeto")
    $Resumo.Add("")

    $TotalAnalisadas = 0
    $TotalHigh = 0
    $TotalCritical = 0
    $Falhas = 0

    Write-Host "`n===== 5. ANALISANDO IMAGENS =====" -ForegroundColor Cyan

    foreach ($Servico in $Servicos) {

        $Imagem = "alura-cicd-${Servico}:1.0"

        Write-Host "`n----------------------------------------" -ForegroundColor Cyan
        Write-Host "SERVICO: $Servico" -ForegroundColor Cyan
        Write-Host "IMAGEM: $Imagem"

        if ($ImagensLocais -notcontains $Imagem) {

            Write-Host "IMAGEM LOCAL NAO ENCONTRADA" -ForegroundColor Yellow

            $Resumo.Add("$Servico | NAO ANALISADO | imagem ausente")
            $Falhas++

            continue
        }

        $ArquivoJSON = Join-Path $Relatorios "$Servico-trivy.json"

        Write-Host "EXECUTANDO SCAN HIGH E CRITICAL..." -ForegroundColor Cyan

        & $Trivy image `
            --image-src docker `
            --scanners vuln `
            --severity HIGH,CRITICAL `
            --format json `
            --output $ArquivoJSON `
            --exit-code 0 `
            $Imagem

        if ($LASTEXITCODE -ne 0) {

            Write-Host "FALHA NO SCAN: $Servico" -ForegroundColor Red

            $Resumo.Add("$Servico | FALHA NA ANALISE")
            $Falhas++

            continue
        }

        if (!(Test-Path $ArquivoJSON -PathType Leaf)) {
            Write-Host "RELATORIO JSON AUSENTE" -ForegroundColor Red

            $Resumo.Add("$Servico | RELATORIO AUSENTE")
            $Falhas++

            continue
        }

        $Dados = Get-Content -LiteralPath $ArquivoJSON -Raw |
            ConvertFrom-Json

        $High = 0
        $Critical = 0

        foreach ($Resultado in @($Dados.Results)) {

            foreach ($Vulnerabilidade in @($Resultado.Vulnerabilities)) {

                if ($null -eq $Vulnerabilidade) {
                    continue
                }

                switch ($Vulnerabilidade.Severity) {
                    "HIGH" {
                        $High++
                    }
                    "CRITICAL" {
                        $Critical++
                    }
                }
            }
        }

        $TotalAnalisadas++
        $TotalHigh += $High
        $TotalCritical += $Critical

        Write-Host "SCAN CONCLUIDO: $Servico" -ForegroundColor Green
        Write-Host "HIGH: $High" -ForegroundColor Yellow
        Write-Host "CRITICAL: $Critical" -ForegroundColor Yellow

        $Resumo.Add("$Servico | HIGH: $High | CRITICAL: $Critical")
    }

    Write-Host "`n===== 6. SALVANDO RELATORIO CONSOLIDADO =====" -ForegroundColor Cyan

    $Resumo.Add("")
    $Resumo.Add("IMAGENS ANALISADAS: $TotalAnalisadas/4")
    $Resumo.Add("TOTAL HIGH: $TotalHigh")
    $Resumo.Add("TOTAL CRITICAL: $TotalCritical")
    $Resumo.Add("IMAGENS AUSENTES OU FALHAS: $Falhas")
    $Resumo.Add("")
    $Resumo.Add("Nenhuma vulnerabilidade foi corrigida automaticamente.")
    $Resumo.Add("Nenhuma imagem foi publicada.")
    $Resumo.Add("Nenhum container foi alterado.")
    $Resumo.Add("Nenhum deploy foi realizado.")

    $ArquivoResumo = Join-Path $Relatorios "aula-218716-resumo-trivy.txt"

    $UTF8 = New-Object System.Text.UTF8Encoding($false)

    [IO.File]::WriteAllLines(
        $ArquivoResumo,
        [string[]]$Resumo.ToArray(),
        $UTF8
    )

    Write-Host "`n===== RESULTADO FINAL =====" -ForegroundColor Green

    Write-Host "IMAGENS ANALISADAS: $TotalAnalisadas/4"
    Write-Host "TOTAL HIGH: $TotalHigh"
    Write-Host "TOTAL CRITICAL: $TotalCritical"
    Write-Host "FALHAS OU AUSENCIAS: $Falhas"
    Write-Host "RELATORIO: $ArquivoResumo"
    Write-Host "Nenhum codigo publicado."
    Write-Host "Nenhuma imagem publicada."
    Write-Host "Nenhum container alterado."
    Write-Host "Nenhum deploy executado."

    if ($Falhas -gt 0) {
        throw "A analise nao foi concluida para todos os servicos. Consulte o resumo."
    }
}
