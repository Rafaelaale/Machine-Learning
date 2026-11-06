"""Executa os testes de churn com cobertura isolada.

Importa dependencias nativas antes de ativar o rastreamento.
"""

import os
import sys
from pathlib import Path

os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
os.environ["COVERAGE_CORE"] = "pytrace"

import numpy
import pandas
import pytest
import coverage


BASE = Path(__file__).resolve().parent.parent
CORE = (
    BASE
    / "projetos"
    / "churn_profissional"
    / "src"
    / "tratamentos"
    / "pre_processamento"
    / "core.py"
)
TESTE = BASE / "tests" / "test_aula12_pytest.py"
RESULTADOS = BASE / "resultados"


def main() -> int:
    """Mede testes e cobertura apenas do modulo selecionado."""
    RESULTADOS.mkdir(parents=True, exist_ok=True)

    print("===== DEPENDENCIAS PRE-CARREGADAS =====")
    print("Python:", sys.version.split()[0])
    print("NumPy:", numpy.__version__)
    print("Pandas:", pandas.__version__)
    print("Pytest:", pytest.__version__)
    print("Coverage:", coverage.__version__)

    cobertura = coverage.Coverage(
        include=[str(CORE)],
        branch=True,
        data_file=str(RESULTADOS / ".coverage_aula12"),
    )

    print("\n===== INICIANDO COBERTURA =====", flush=True)

    cobertura.start()

    try:
        resultado = pytest.main([
            str(TESTE),
            "-q",
            "-p",
            "no:cov",
        ])
    finally:
        cobertura.stop()
        cobertura.save()

    if resultado != 0:
        print("\nTestes falharam. Cobertura nao aprovada.")
        return int(resultado)

    print("\n===== RELATORIO DE COBERTURA =====")
    cobertura.report(show_missing=True)

    arquivo_json = (
        RESULTADOS / "aula12_cobertura.json"
    )
    arquivo_xml = (
        RESULTADOS / "aula12_cobertura.xml"
    )

    cobertura.json_report(outfile=str(arquivo_json))
    cobertura.xml_report(outfile=str(arquivo_xml))

    import json

    relatorio = json.loads(
        arquivo_json.read_text(encoding="utf-8")
    )

    totais = relatorio["totals"]
    percentual = totais["percent_covered"]

    print("\n===== RESULTADO FINAL =====")
    print(f"Cobertura combinada: {percentual:.2f}%")
    print("Linhas cobertas:", totais["covered_lines"])
    print("Linhas executaveis:", totais["num_statements"])
    print(
        "Branches cobertos:",
        totais.get("covered_branches", 0),
    )
    print(
        "Branches totais:",
        totais.get("num_branches", 0),
    )

    if percentual < 85:
        print(
            "ATENCAO: cobertura abaixo da meta didatica de 85%."
        )
    else:
        print("META DE COBERTURA ATINGIDA.")

    print("Relatorio JSON:", arquivo_json)
    print("Relatorio XML:", arquivo_xml)

    return 0


if __name__ == "__main__":
    sys.exit(main())
