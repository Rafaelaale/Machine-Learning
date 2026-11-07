"""Auditoria do projeto de series temporais.

Somente leitura dos arquivos das aulas.
Produz relatorios na pasta resultados.
"""

import ast
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

import pandas as pd
import numpy as np


RAIZ = Path(__file__).resolve().parent.parent
SAIDA = RAIZ / "resultados"
SAIDA.mkdir(exist_ok=True)

EXTENSOES = {
    ".py", ".ipynb", ".md", ".csv",
    ".json", ".html", ".txt", ".pkl"
}

IGNORAR = {
    "__pycache__",
    ".pytest_cache",
    ".git",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    ".venv-rota",
    "venv",
    "node_modules",
}

ERROS = []
AVISOS = []
INVENTARIO = []
COBERTURA = defaultdict(list)
CONTAGEM = Counter()

CELULAS_CODIGO = 0
PYTHON_VALIDOS = 0
NOTEBOOKS_VALIDOS = 0

OBRIGATORIOS = [
    "app.py",
    "src/aula14_preparacao_exogenas_sarimax.py",
    "src/aula15_treinamento_sarimax.py",
    "src/aula16_preparacao_streamlit.py",
    "src/aula17_app_utils.py",
    "notebooks/14_variaveis_exogenas_sarimax.ipynb",
    "notebooks/15_treinamento_sarimax.ipynb",
    "notebooks/16_preparacao_aplicacao_streamlit.ipynb",
    "notebooks/17_explorando_app_streamlit.ipynb",
    "outputs/tabelas/serie_historica.csv",
    "outputs/tabelas/metricas.csv",
    "outputs/tabelas/previsoes.csv",
    "outputs/tabelas/resumo_projeto.csv",
    "modelos/aula15_sarimax_111_1017.pkl",
]

print("\n===== AUDITORIA COMPLETA =====")

print("\n1. INVENTARIO")

for arquivo in sorted(RAIZ.rglob("*")):
    if not arquivo.is_file():
        continue

    relativo = arquivo.relative_to(RAIZ)

    if any(
        parte in IGNORAR or parte.startswith(".venv")
        for parte in relativo.parts
    ):
        continue

    if arquivo.suffix.lower() not in EXTENSOES:
        continue

    nome = relativo.as_posix()
    tamanho = arquivo.stat().st_size

    INVENTARIO.append({
        "nome": nome,
        "extensao": arquivo.suffix.lower(),
        "bytes": tamanho,
    })

    CONTAGEM[arquivo.suffix.lower()] += 1

    if tamanho == 0:
        ERROS.append(f"Arquivo vazio: {nome}")

    encontrado = re.search(
        r"(?:aula|test_aula)[_-]?0?(\d{1,2})(?!\d)",
        arquivo.stem,
        flags=re.IGNORECASE,
    )

    if encontrado:
        COBERTURA[int(encontrado.group(1))].append(nome)

    if arquivo.suffix.lower() == ".ipynb":
        encontrado_numero = re.match(
            r"^(\d{1,2})_",
            arquivo.stem,
        )

        if encontrado_numero:
            numero = int(encontrado_numero.group(1))
            COBERTURA[numero].append(nome)

    if arquivo.suffix.lower() == ".py":
        try:
            texto = arquivo.read_text(
                encoding="utf-8-sig"
            )
            ast.parse(texto, filename=nome)
            PYTHON_VALIDOS += 1

        except Exception as exc:
            ERROS.append(
                f"Erro Python em {nome}: {exc}"
            )

    elif arquivo.suffix.lower() == ".ipynb":
        try:
            notebook = json.loads(
                arquivo.read_text(
                    encoding="utf-8-sig"
                )
            )

            celulas = notebook.get("cells", [])

            if not isinstance(celulas, list):
                raise ValueError(
                    "Lista de celulas invalida."
                )

            quantidade = 0

            for indice, celula in enumerate(celulas, 1):
                if celula.get("cell_type") != "code":
                    continue

                fonte = celula.get("source", "")
                texto = (
                    "".join(fonte)
                    if isinstance(fonte, list)
                    else str(fonte)
                )

                if not texto.strip():
                    continue

                quantidade += 1
                CELULAS_CODIGO += 1

                linhas = texto.splitlines()

                # Magics do Jupyter nao sao Python puro.
                if any(
                    linha.lstrip().startswith(
                        ("%", "!", "?")
                    )
                    for linha in linhas
                ):
                    AVISOS.append(
                        f"Celula Jupyter especial: "
                        f"{nome}, celula {indice}"
                    )
                    continue

                try:
                    ast.parse(texto)
                except SyntaxError as exc:
                    ERROS.append(
                        f"Notebook {nome}, "
                        f"celula {indice}: {exc}"
                    )

            NOTEBOOKS_VALIDOS += 1

            if quantidade == 0:
                AVISOS.append(
                    f"Notebook sem celulas Python: {nome}"
                )

        except Exception as exc:
            ERROS.append(
                f"Notebook invalido {nome}: {exc}"
            )

for extensao, total in sorted(CONTAGEM.items()):
    print(f"{extensao}: {total}")

print("\n2. ARQUIVOS OBRIGATORIOS")

for nome in OBRIGATORIOS:
    arquivo = RAIZ / nome

    if arquivo.is_file() and arquivo.stat().st_size > 0:
        print("OK:", nome)
    else:
        print("AUSENTE:", nome)
        ERROS.append(
            f"Arquivo obrigatorio ausente: {nome}"
        )

print("\n3. COBERTURA DAS AULAS")

for numero in range(1, 18):
    encontrados = sorted(
        set(COBERTURA.get(numero, []))
    )

    print(
        f"AULA {numero:02d}: "
        f"{len(encontrados)} arquivo(s)"
    )

    if not encontrados:
        AVISOS.append(
            f"Aula {numero:02d}: nenhum arquivo "
            "identificado pela nomenclatura."
        )

print("\n4. VALIDANDO CSVs DO APLICATIVO")

try:
    pasta = RAIZ / "outputs" / "tabelas"

    historico = pd.read_csv(
        pasta / "serie_historica.csv",
        parse_dates=["data_hora"],
    )

    metricas = pd.read_csv(
        pasta / "metricas.csv"
    )

    previsoes = pd.read_csv(
        pasta / "previsoes.csv",
        parse_dates=["data_hora"],
    )

    resumo = pd.read_csv(
        pasta / "resumo_projeto.csv"
    )

    assert len(historico) == 456
    assert len(metricas) == 4
    assert len(previsoes) == 60
    assert len(resumo) == 1

    assert {
        "data_hora", "demanda"
    }.issubset(historico.columns)

    assert {
        "modelo", "MAE", "RMSE", "MAPE"
    }.issubset(metricas.columns)

    assert {
        "data_hora",
        "demanda",
        "previsao_baseline",
        "previsao_arima",
        "previsao_sarima",
        "previsao_sarimax",
    }.issubset(previsoes.columns)

    assert {
        "modelo_final",
        "MAE",
        "RMSE",
        "MAPE",
        "inicio_historico",
        "fim_historico",
        "dias_historico",
        "dias_teste",
    }.issubset(resumo.columns)

    assert np.isfinite(
        metricas[
            ["MAE", "RMSE", "MAPE"]
        ].to_numpy(dtype=float)
    ).all()

    melhor = (
        metricas.sort_values("MAPE")
        .iloc[0]
    )

    assert (
        resumo.iloc[0]["modelo_final"]
        == melhor["modelo"]
    )

    print("HISTORICO:", len(historico))
    print("MODELOS:", len(metricas))
    print("TESTE:", len(previsoes))
    print("MELHOR MODELO:", melhor["modelo"])
    print("MAPE:", float(melhor["MAPE"]))
    print("DADOS STREAMLIT: OK")

except Exception as exc:
    ERROS.append(
        f"Falha nos CSVs do Streamlit: {exc}"
    )
    print("DADOS STREAMLIT: FALHA", exc)

print("\n5. GERANDO RELATORIOS")

relatorio = {
    "data": datetime.now().isoformat(
        timespec="seconds"
    ),
    "total_arquivos": len(INVENTARIO),
    "contagem": dict(CONTAGEM),
    "python_validos": PYTHON_VALIDOS,
    "notebooks_validos": NOTEBOOKS_VALIDOS,
    "celulas_codigo": CELULAS_CODIGO,
    "aulas": {
        str(numero): sorted(
            set(COBERTURA.get(numero, []))
        )
        for numero in range(1, 18)
    },
    "inventario": INVENTARIO,
    "erros": ERROS,
    "avisos": AVISOS,
}

caminho_json = (
    SAIDA / "auditoria_completa_projeto.json"
)

caminho_txt = (
    SAIDA / "auditoria_completa_projeto.txt"
)

caminho_json.write_text(
    json.dumps(
        relatorio,
        ensure_ascii=False,
        indent=2,
    ),
    encoding="utf-8",
)

linhas = [
    "AUDITORIA COMPLETA DO PROJETO",
    "",
    f"Total de arquivos: {len(INVENTARIO)}",
    f"Python validos: {PYTHON_VALIDOS}",
    f"Notebooks validos: {NOTEBOOKS_VALIDOS}",
    f"Celulas de codigo: {CELULAS_CODIGO}",
    "",
    "COBERTURA POR AULA",
]

for numero in range(1, 18):
    linhas.append(f"\nAULA {numero:02d}")

    localizados = sorted(
        set(COBERTURA.get(numero, []))
    )

    if not localizados:
        linhas.append(
            "Nenhum arquivo identificado pelo nome."
        )

    for nome in localizados:
        linhas.append("  " + nome)

linhas.extend([
    "",
    "ERROS",
    *(ERROS or ["Nenhum"]),
    "",
    "AVISOS",
    *(AVISOS or ["Nenhum"]),
    "",
    "INVENTARIO",
])

for item in INVENTARIO:
    linhas.append(
        f"{item['bytes']:>10} bytes | {item['nome']}"
    )

caminho_txt.write_text(
    "\n".join(linhas) + "\n",
    encoding="utf-8",
)

print("\n===== RESULTADO DA AUDITORIA ESTATICA =====")
print("TOTAL DE ARQUIVOS:", len(INVENTARIO))
print("PYTHON VALIDOS:", PYTHON_VALIDOS)
print("NOTEBOOKS VALIDOS:", NOTEBOOKS_VALIDOS)
print("CELULAS DE CODIGO:", CELULAS_CODIGO)
print("ERROS:", len(ERROS))
print("AVISOS:", len(AVISOS))
print("RELATORIO TXT:", caminho_txt)
print("RELATORIO JSON:", caminho_json)

if ERROS:
    for erro in ERROS:
        print("ERRO:", erro)