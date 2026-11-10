
        param(
            [string]$Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"
        )

        $ErrorActionPreference = "Stop"

        $Repositorio = Join-Path $Projeto "docker-automation"
        $Workflow = Join-Path $Repositorio ".github\workflows\docker-dev-aula-03.yml"
        $Aulas = Join-Path $Projeto "aulas"
        $Notas = Join-Path $Aulas "aula-testes-microservicos-github-actions.txt"
        $UTF8 = New-Object System.Text.UTF8Encoding($false)

        Write-Host "`n===== 1. VERIFICANDO PROJETO =====" -ForegroundColor Cyan

        if (!(Test-Path $Workflow -PathType Leaf)) {
            throw "Workflow da aula anterior nao encontrado."
        }

        foreach ($Servico in @(
            "auth-service",
            "user-service",
            "order-service",
            "product-service"
        )) {
            $Pasta = Join-Path $Repositorio "burguer-app\$Servico"

            foreach ($Arquivo in @("Dockerfile", "requirements.txt")) {
                if (!(Test-Path (Join-Path $Pasta $Arquivo))) {
                    throw "Arquivo nao encontrado: $Servico\$Arquivo"
                }
            }

            $Testes = @(
                Get-ChildItem -LiteralPath $Pasta `
                    -Recurse -File -Filter "test_*.py" `
                    -ErrorAction SilentlyContinue
            )

            if ($Testes.Count -eq 0) {
                throw "Nenhum arquivo de teste encontrado: $Servico"
            }

            Write-Host "CONFIRMADO: $Servico | $($Testes.Count) arquivo(s) de teste" -ForegroundColor Green
        }

        Set-Location $Repositorio

        Write-Host "`n===== 2. VERIFICANDO WORKFLOW ATUAL =====" -ForegroundColor Cyan

        $Atual = [IO.File]::ReadAllText($Workflow)

        $Obrigatorios = @(
            "working-directory: burguer-app",
            "Aguardar inicializacao do MongoDB",
            "Testar conexao dos microservicos com MongoDB",
            "Testar HTTP dos quatro microservicos",
            "Confirmar homologacao",
            "Shut down Docker containers"
        )

        foreach ($Termo in $Obrigatorios) {
            if (!$Atual.Contains($Termo)) {
                throw "Etapa anterior ausente: $Termo"
            }
        }

        Write-Host "WORKFLOW ORIGINAL DA AULA ENCONTRADO" -ForegroundColor Green

        Write-Host "`n===== 3. PREPARANDO QUATRO ETAPAS DE TESTE =====" -ForegroundColor Cyan

        $Etapas = @'
      - name: Configurar Python para testes
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Test auth-service
        working-directory: burguer-app/auth-service
        run: |
          python -m pip install --upgrade pip
          python -m pip install -r requirements.txt
          python -m pip install pytest pytest-cov
          python -m pytest -v --cov=. --cov-report=term-missing --cov-branch

      - name: Test user-service
        working-directory: burguer-app/user-service
        run: |
          python -m pip install -r requirements.txt
          python -m pip install pytest
          python -m pytest -v

      - name: Test order-service
        working-directory: burguer-app/order-service
        run: |
          python -m pip install -r requirements.txt
          python -m pip install pytest
          python -m pytest -v

      - name: Test product-service
        working-directory: burguer-app/product-service
        run: |
          python -m pip install -r requirements.txt
          python -m pip install pytest
          python -m pytest -v

'@

        $NomesTestes = @(
            "Test auth-service",
            "Test user-service",
            "Test order-service",
            "Test product-service"
        )

        $Presentes = @(
            foreach ($Nome in $NomesTestes) {
                if ($Atual -match "(?m)^      - name: $([regex]::Escape($Nome))\s*$") {
                    $Nome
                }
            }
        )

        if ($Presentes.Count -eq 4) {
            Write-Host "QUATRO ETAPAS JA EXISTEM. ARQUIVO PRESERVADO." -ForegroundColor Yellow
            $Final = $Atual
        }
        elseif ($Presentes.Count -gt 0) {
            throw "Workflow contem testes parciais. Nenhuma alteracao realizada."
        }
        else {
            Write-Host "`n===== 4. CRIANDO BACKUP =====" -ForegroundColor Cyan

            New-Item -ItemType Directory -Force -Path $Aulas | Out-Null

            $Backup = Join-Path $Aulas (
                "backup-docker-dev-aula03-" +
                (Get-Date -Format "yyyyMMdd-HHmmss") +
                ".yml"
            )

            Copy-Item -LiteralPath $Workflow -Destination $Backup

            Write-Host "BACKUP: $Backup" -ForegroundColor Green

            Write-Host "`n===== 5. ADICIONANDO TESTES AO PIPELINE =====" -ForegroundColor Cyan

            $Marcador = "      - name: Confirmar homologacao"

            $Ocorrencias = [regex]::Matches(
                $Atual,
                [regex]::Escape($Marcador)
            ).Count

            if ($Ocorrencias -ne 1) {
                throw "Nao foi possivel identificar o ponto de insercao com seguranca."
            }

            $Quebra = if ($Atual.Contains("`r`n")) {
                "`r`n"
            }
            else {
                "`n"
            }

            $TextoEtapas = $Etapas.TrimEnd() -replace "`r`n", "`n"
            $TextoEtapas = $TextoEtapas.Replace("`n", $Quebra)

            $Final = $Atual.Replace(
                $Marcador,
                $TextoEtapas + $Quebra + $Quebra + $Marcador
            )

            [IO.File]::WriteAllText($Workflow, $Final, $UTF8)

            Write-Host "QUATRO ETAPAS ADICIONADAS" -ForegroundColor Green
        }

        Write-Host "`n===== 6. VALIDANDO ESTRUTURA =====" -ForegroundColor Cyan

        $Final = [IO.File]::ReadAllText($Workflow)

        foreach ($Nome in $NomesTestes) {
            $Padrao = "(?m)^      - name: $([regex]::Escape($Nome))\s*$"

            $Quantidade = [regex]::Matches($Final, $Padrao).Count

            if ($Quantidade -ne 1) {
                throw "Teste ausente ou duplicado: $Nome"
            }

            Write-Host "VALIDADO: $Nome" -ForegroundColor Green
        }

        foreach ($Servico in @(
            "auth-service",
            "user-service",
            "order-service",
            "product-service"
        )) {
            $Diretorio = "working-directory: burguer-app/$Servico"

            if (!$Final.Contains($Diretorio)) {
                throw "Diretorio incorreto: $Servico"
            }
        }

        $EtapasOrdem = @(
            "      - name: Aguardar inicializacao do MongoDB",
            "      - name: Testar conexao dos microservicos com MongoDB",
            "      - name: Testar HTTP dos quatro microservicos",
            "      - name: Configurar Python para testes",
            "      - name: Test auth-service",
            "      - name: Test user-service",
            "      - name: Test order-service",
            "      - name: Test product-service",
            "      - name: Confirmar homologacao",
            "      - name: Shut down Docker containers"
        )

        $UltimoIndice = -1

        foreach ($Nome in $EtapasOrdem) {
            $Indice = $Final.IndexOf($Nome)

            if ($Indice -le $UltimoIndice) {
                throw "Ordem incorreta ou etapa ausente: $Nome"
            }

            $UltimoIndice = $Indice
        }

        if (!$Final.Contains("if: always()")) {
            throw "Encerramento automatico nao encontrado."
        }

        Write-Host "ORDEM DAS ETAPAS VALIDADA" -ForegroundColor Green
        Write-Host "DIRETORIOS DOS SERVICOS VALIDADOS" -ForegroundColor Green

        Write-Host "`n===== 7. SALVANDO ANOTACOES =====" -ForegroundColor Cyan

        $ConteudoNotas = @(
            "AULA - TESTES AUTOMATIZADOS NO DOCKER GITHUB ACTIONS",
            "",
            "OBJETIVO:",
            "Adicionar quatro etapas de teste ao pipeline de homologacao.",
            "",
            "ORDEM DE EXECUCAO:",
            "1. Checkout do repositorio.",
            "2. Preparar variaveis de ambiente.",
            "3. Construir containers com Docker Compose.",
            "4. Aguardar MongoDB.",
            "5. Validar MongoDB e HTTP.",
            "6. Configurar Python.",
            "7. Testar auth-service com pytest e cobertura.",
            "8. Testar user-service com pytest.",
            "9. Testar order-service com pytest.",
            "10. Testar product-service com pytest.",
            "11. Finalizar homologacao.",
            "12. Encerrar containers.",
            "",
            "COMANDO DE COBERTURA DA AULA:",
            "python -m pytest -v --cov=. --cov-report=term-missing --cov-branch",
            "",
            "OBSERVACAO SOBRE 90 POR CENTO:",
            "O professor utiliza --cov-fail-under=90.",
            "Esse limite nao foi ativado porque a cobertura anterior",
            "do projeto ainda nao atingiu esse percentual.",
            "O relatorio mostrara a cobertura efetivamente medida.",
            "",
            "SITUACAO:",
            "Workflow preparado localmente.",
            "Testes ainda nao executados no GitHub Actions.",
            "O projeto sera publicado somente no final do curso.",
            "Nenhum git add, commit ou push.",
            "Nenhum deploy em producao."
        )

        if (!(Test-Path $Notas)) {
            [IO.File]::WriteAllLines($Notas, $ConteudoNotas, $UTF8)
            Write-Host "ANOTACOES SALVAS" -ForegroundColor Green
        }
        else {
            Write-Host "ANOTACOES EXISTENTES PRESERVADAS"
        }

        Write-Host "`n===== 8. ABRINDO NO VS CODE =====" -ForegroundColor Cyan

        if (Get-Command code -ErrorAction SilentlyContinue) {
            code -r $Workflow $Notas
        }

        Write-Host "`n===== RESULTADO FINAL =====" -ForegroundColor Green

        Write-Host "QUATRO TESTES CONFIGURADOS."
        Write-Host "COBERTURA CONFIGURADA PARA AUTH-SERVICE."
        Write-Host "WORKFLOW: $Workflow"
        Write-Host "TESTES AINDA NAO EXECUTADOS NO GITHUB ACTIONS."
        Write-Host "NENHUM GIT ADD, COMMIT OU PUSH."
        Write-Host "NENHUM CONTAINER LOCAL ALTERADO."
