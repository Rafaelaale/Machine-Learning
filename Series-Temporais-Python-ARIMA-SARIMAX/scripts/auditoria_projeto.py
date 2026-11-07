"""Auditoria de integridade das Aulas 02 a 06."""

import ast
import csv
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "resultados"
SAIDA.mkdir(parents=True, exist_ok=True)

ARQUIVOS = {
    "Aula 02": [
        "src/visual_utils.py",
        "src/preparacao_bikes.py",
        "aulas/aula02_validacao_preparacao.py",
        "tests/test_aula02_validacao_preparacao.py",
        "anotacoes/aula02_validacao_preparacao.md",
        "notebooks/01_validacao_ambiente.ipynb",
        "notebooks/02_preparacao_bikes.ipynb",
        "dados/bike_tratado.csv",
        "graficos/demanda_bicicletas.html",
        "resultados/aula02_validacao.json",
    ],
    "Aula 03": [
        "src/analise_exploratoria.py",
        "aulas/aula03_analise_exploratoria.py",
        "tests/test_aula03_analise_exploratoria.py",
        "anotacoes/aula03_analise_exploratoria.md",
        "notebooks/03_analise_exploratoria_temporal.ipynb",
        "resultados/serie_diaria_bike.csv",
        "resultados/aula03_analise_exploratoria.json",
        "graficos/01_demanda_horaria.html",
        "graficos/02_demanda_diaria.html",
        "graficos/03_media_por_hora.html",
        "graficos/04_media_por_dia_semana.html",
        "graficos/05_media_por_mes.html",
    ],
    "Aula 04": [
        "src/aula04_decomposicao.py",
        "aulas/aula04_decomposicao.py",
        "tests/test_aula04_decomposicao.py",
        "anotacoes/aula04_decomposicao.md",
        "notebooks/04_tendencia_sazonalidade_ruido.ipynb",
        "resultados/aula04_media_movel.csv",
        "resultados/aula04_componentes.csv",
        "resultados/aula04_decomposicao.json",
        "graficos/aula04_media_movel.html",
        "graficos/aula04_decomposicao.html",
    ],
    "Aula 05": [
        "src/aula05_adf.py",
        "aulas/aula05_adf.py",
        "tests/test_aula05_adf.py",
        "anotacoes/aula05_adf.md",
        "notebooks/05_teste_adf.ipynb",
        "resultados/resultados_adf_original.csv",
        "resultados/aula05_adf.json",
    ],
    "Aula 06": [
        "src/aula06_diferenciacao.py",
        "aulas/aula06_diferenciacao.py",
        "tests/test_aula06_diferenciacao.py",
        "anotacoes/aula06_diferenciacao.md",
        "notebooks/06_diferenciacao_estacionariedade.ipynb",
        "resultados/aula06_serie_diferenciada.csv",
        "resultados/aula06_adf_diferenciado.csv",
        "resultados/aula06_comparacao_adf.csv",
        "resultados/aula06_diferenciacao.json",
        "graficos/aula06_original_vs_diferenciada.html",
    ],
}

registros = []
observacoes = []


def registrar(aula, arquivo, status, detalhe=""):
    registros.append({
        "aula": aula,
        "arquivo": arquivo,
        "status": status,
        "detalhe": detalhe,
    })

    print(f"[{status}] {aula}: {arquivo}")


print("\n===== 1. CONFERINDO ARQUIVOS =====")

for aula, arquivos in ARQUIVOS.items():
    for nome in arquivos:
        caminho = RAIZ / nome

        if not caminho.is_file():
            registrar(aula, nome, "AUSENTE")
            continue

        if caminho.stat().st_size == 0:
            registrar(aula, nome, "VAZIO")
            continue

        try:
            if caminho.suffix == ".py":
                texto = caminho.read_text(encoding="utf-8-sig")
                ast.parse(texto, filename=str(caminho))

            elif caminho.suffix == ".ipynb":
                notebook = json.loads(
                    caminho.read_text(encoding="utf-8-sig")
                )

                if notebook.get("nbformat") != 4:
                    raise ValueError("Formato notebook invalido.")

                celulas = notebook.get("cells", [])

                if not celulas:
                    raise ValueError("Notebook sem celulas.")

                codigo_celulas = [
                    cel for cel in celulas
                    if cel.get("cell_type") == "code"
                ]

                if not codigo_celulas:
                    raise ValueError("Notebook sem codigo.")

                for cel in codigo_celulas:
                    fonte = cel.get("source", [])
                    if isinstance(fonte, list):
                        fonte = "".join(fonte)
                    ast.parse(fonte)

            elif caminho.suffix == ".json":
                json.loads(
                    caminho.read_text(encoding="utf-8-sig")
                )

            elif caminho.suffix == ".csv":
                with caminho.open(
                    encoding="utf-8-sig",
                    newline="",
                ) as f:
                    leitor = csv.reader(f)
                    cabecalho = next(leitor, None)
                    primeira = next(leitor, None)

                if not cabecalho or primeira is None:
                    raise ValueError("CSV sem dados.")

            registrar(aula, nome, "OK")

        except Exception as erro:
            registrar(
                aula,
                nome,
                "ERRO",
                str(erro),
            )


print("\n===== 2. BASE ORIGINAL =====")

bike = RAIZ / "dados" / "bike.csv"

if bike.is_file():
    try:
        import pandas as pd

        df = pd.read_csv(bike)
        print("Registros:", len(df))
        print("Colunas:", len(df.columns))

        if len(df) != 10886 or len(df.columns) != 12:
            observacoes.append(
                "bike.csv possui dimensoes diferentes das "
                "10886 linhas e 12 colunas esperadas."
            )
        else:
            print("BASE ORIGINAL: VALIDADA")

    except Exception as erro:
        observacoes.append(
            f"Erro ao ler bike.csv: {erro}"
        )
else:
    observacoes.append(
        "CRITICO: dados/bike.csv nao encontrado."
    )


print("\n===== 3. AMBIENTE VIRTUAL =====")

bibliotecas = [
    "pandas",
    "numpy",
    "plotly",
    "statsmodels",
    "scipy",
    "sklearn",
    "pytest",
    "ipykernel",
]

import importlib

for nome in bibliotecas:
    try:
        modulo = importlib.import_module(nome)
        versao = getattr(modulo, "__version__", "instalado")
        print(f"[OK] {nome}: {versao}")
    except Exception as erro:
        print(f"[ERRO] {nome}: {erro}")
        observacoes.append(
            f"Biblioteca indisponivel: {nome}"
        )


print("\n===== 4. TESTES AUTOMATIZADOS =====")

testes = {}

for numero in range(2, 7):
    aula = f"Aula {numero:02d}"
    padrao = f"test_aula{numero:02d}_*.py"

    existentes = list((RAIZ / "tests").glob(padrao))

    if not existentes:
        testes[aula] = {
            "status": "NAO ENCONTRADOS",
            "quantidade_arquivos": 0,
        }
        print(f"[AUSENTE] {aula}: testes nao encontrados")
        continue

    comando = [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        "tests",
        "-p",
        padrao,
        "-v",
    ]

    try:
        processo = subprocess.run(
            comando,
            cwd=RAIZ,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )

        log = (
            processo.stdout
            + "\n"
            + processo.stderr
        )

        caminho_log = (
            SAIDA / f"auditoria_testes_aula{numero:02d}.txt"
        )
        caminho_log.write_text(
            log,
            encoding="utf-8",
        )

        sucesso = processo.returncode == 0

        testes[aula] = {
            "status": "APROVADO" if sucesso else "FALHOU",
            "quantidade_arquivos": len(existentes),
            "log": str(caminho_log.relative_to(RAIZ)),
        }

        print(
            f"{aula}:",
            testes[aula]["status"],
        )

        if not sucesso:
            observacoes.append(
                f"{aula}: testes com falhas. "
                f"Ver {caminho_log.name}."
            )

    except subprocess.TimeoutExpired:
        testes[aula] = {"status": "TEMPO ESGOTADO"}
        observacoes.append(
            f"{aula}: testes excederam 120 segundos."
        )


print("\n===== 5. ORGANIZACAO DO PROJETO =====")

pastas = [
    "src",
    "aulas",
    "tests",
    "notebooks",
    "dados",
    "resultados",
    "graficos",
    "anotacoes",
]

for pasta in pastas:
    caminho = RAIZ / pasta

    print(
        "[OK]" if caminho.is_dir() else "[AUSENTE]",
        pasta,
    )


print("\n===== 6. GERANDO RELATORIO =====")

total = len(registros)
aprovados = sum(
    r["status"] == "OK" for r in registros
)
ausentes = [
    r for r in registros if r["status"] != "OK"
]

resumo_aulas = {}

for aula in ARQUIVOS:
    itens = [
        r for r in registros if r["aula"] == aula
    ]

    resumo_aulas[aula] = {
        "arquivos_esperados": len(itens),
        "arquivos_ok": sum(
            r["status"] == "OK" for r in itens
        ),
        "pendencias": [
            r["arquivo"] for r in itens
            if r["status"] != "OK"
        ],
        "testes": testes.get(aula),
    }

relatorio = {
    "data_auditoria": datetime.now().isoformat(
        timespec="seconds"
    ),
    "projeto": str(RAIZ),
    "arquivos_verificados": total,
    "arquivos_aprovados": aprovados,
    "arquivos_com_pendencias": len(ausentes),
    "aulas": resumo_aulas,
    "detalhes": registros,
    "observacoes": observacoes,
}

arquivo_json = SAIDA / "auditoria_completa.json"

arquivo_json.write_text(
    json.dumps(
        relatorio,
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)

linhas = [
    "# Auditoria geral — Séries Temporais",
    "",
    f"Data: {relatorio['data_auditoria']}",
    "",
    f"Projeto: `{RAIZ}`",
    "",
    "## Resumo",
    "",
    f"- Arquivos verificados: {total}",
    f"- Arquivos aprovados: {aprovados}",
    f"- Arquivos com pendencias: {len(ausentes)}",
    "",
    "## Resultado por aula",
    "",
]

for aula, dados in resumo_aulas.items():
    linhas.extend([
        f"### {aula}",
        f"Arquivos: {dados['arquivos_ok']}"
        f"/{dados['arquivos_esperados']}",
        f"Testes: {dados['testes']['status']}",
        "",
    ])

linhas.extend([
    "## Arquivos pendentes",
    "",
])

if ausentes:
    for item in ausentes:
        linhas.append(
            f"- {item['aula']}: "
            f"`{item['arquivo']}` "
            f"— {item['status']} "
            f"{item['detalhe']}"
        )
else:
    linhas.append("Nenhum arquivo pendente.")

linhas.extend([
    "",
    "## Observacoes",
    "",
])

if observacoes:
    for observacao in observacoes:
        linhas.append(f"- {observacao}")
else:
    linhas.append("Nenhuma observacao adicional.")

linhas.extend([
    "",
    "## Escopo",
    "",
    "A auditoria verifica existencia, formato, sintaxe,",
    "integridade basica e execucao dos testes presentes.",
    "Ela nao comprova que todo conteudo de cada",
    "transcricao foi implementado integralmente.",
    "",
    "Nenhum arquivo das aulas foi substituido.",
])

arquivo_md = SAIDA / "AUDITORIA_GERAL_VSCODE.md"

arquivo_md.write_text(
    "\n".join(linhas) + "\n",
    encoding="utf-8",
)

print("\n===== RESULTADO FINAL =====")
print("Arquivos verificados:", total)
print("Arquivos aprovados:", aprovados)
print("Pendencias:", len(ausentes))
print("Relatorio Markdown:", arquivo_md)
print("Relatorio JSON:", arquivo_json)

if ausentes or any(
    t.get("status") != "APROVADO"
    for t in testes.values()
):
    print("\nAUDITORIA FINALIZADA COM PENDENCIAS.")
else:
    print("\nAUDITORIA FINALIZADA SEM PENDENCIAS DE ARQUIVOS OU TESTES.")
