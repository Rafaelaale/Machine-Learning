& {
    $ErrorActionPreference = "Stop"

    $Projeto = "F:\Projetos\Docker-GitHubActions-CI-CD"

    $Notas = Join-Path $Projeto "aulas\versionamento\aula-218717-conceitos-versionamento.txt"
    $Exemplos = Join-Path $Projeto "aulas\versionamento\exemplos-semver.txt"

    Write-Host "`n===== VALIDANDO ARQUIVOS =====" -ForegroundColor Cyan

    foreach ($Arquivo in @($Notas, $Exemplos)) {
        if (!(Test-Path $Arquivo -PathType Leaf)) {
            throw "Arquivo nao encontrado: $Arquivo"
        }

        Write-Host "ENCONTRADO: $([IO.Path]::GetFileName($Arquivo))" -ForegroundColor Green
    }

    Write-Host "`n===== VALIDANDO CONCEITOS =====" -ForegroundColor Cyan

    $Texto = [IO.File]::ReadAllText($Notas)

    $Conceitos = @(
        "VERSIONAMENTO",
        "SEMVER",
        "MAJOR",
        "MINOR",
        "PATCH",
        "PRE-RELEASE",
        "BUILD METADATA",
        "TAGS",
        "GITFLOW",
        "FEATURE",
        "RELEASE",
        "HOTFIX",
        "ROLLBACK",
        "OBSERVABILIDADE",
        "LOGS",
        "METRICAS",
        "TRACES"
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

    Write-Host "`n===== VALIDANDO VERSOES SEMVER =====" -ForegroundColor Cyan

    $Numero = '(0|[1-9][0-9]*)'
    $Pre = '(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)'
    $Identificador = '[0-9A-Za-z-]+'

    $Padrao = '^(?:v)?' +
        $Numero + '\.' + $Numero + '\.' + $Numero +
        '(?:-' + $Pre + '(?:\.' + $Pre + ')*)?' +
        '(?:\+' + $Identificador + '(?:\.' + $Identificador + ')*)?$'

    $Validas = @(
        "1.0.0",
        "1.1.0",
        "1.1.1",
        "2.0.0",
        "1.8.5-rc.1",
        "1.8.5+build.123",
        "v1.8.5"
    )

    $Invalidas = @(
        "1.8",
        "1.8.5.1",
        "v1.8.5.1",
        "01.2.3"
    )

    foreach ($Versao in $Validas) {
        if ($Versao -cnotmatch $Padrao) {
            throw "Versao deveria ser valida: $Versao"
        }

        Write-Host "SEMVER VALIDO: $Versao" -ForegroundColor Green
    }

    foreach ($Versao in $Invalidas) {
        if ($Versao -cmatch $Padrao) {
            throw "Versao deveria ser invalida: $Versao"
        }

        Write-Host "SEMVER INVALIDO IDENTIFICADO: $Versao" -ForegroundColor Yellow
    }

    Write-Host "`n===== VALIDANDO EVOLUCAO DE VERSOES =====" -ForegroundColor Cyan

    $Cenarios = @(
        @{ De = "1.0.0"; Para = "1.0.1"; Tipo = "PATCH" },
        @{ De = "1.0.1"; Para = "1.1.0"; Tipo = "MINOR" },
        @{ De = "1.1.0"; Para = "2.0.0"; Tipo = "MAJOR" }
    )

    foreach ($Cenario in $Cenarios) {
        $Anterior = [version]$Cenario.De
        $Atual = [version]$Cenario.Para

        if ($Atual.Major -gt $Anterior.Major) {
            $Tipo = "MAJOR"
        }
        elseif ($Atual.Minor -gt $Anterior.Minor) {
            $Tipo = "MINOR"
        }
        elseif ($Atual.Build -gt $Anterior.Build) {
            $Tipo = "PATCH"
        }
        else {
            throw "Evolucao nao reconhecida."
        }

        if ($Tipo -ne $Cenario.Tipo) {
            throw "Classificacao incorreta."
        }

        Write-Host "$($Cenario.De) -> $($Cenario.Para): $Tipo" -ForegroundColor Green
    }

    Write-Host "`n===== RESULTADO FINAL =====" -ForegroundColor Green

    Write-Host "CONCEITOS VALIDADOS: $($Conceitos.Count)"
    Write-Host "VERSOES VALIDAS TESTADAS: $($Validas.Count)"
    Write-Host "VERSOES INVALIDAS IDENTIFICADAS: $($Invalidas.Count)"
    Write-Host "EVOLUCOES CLASSIFICADAS: $($Cenarios.Count)"
    Write-Host "Nenhuma branch ou tag criada."
    Write-Host "Nenhum repositorio alterado."
    Write-Host "Nenhum codigo publicado."
    Write-Host "Nenhum deploy executado."
}
