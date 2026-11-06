"""Executa a auditoria didatica de versionamento."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula13_versionamento import (
    auditar_projeto,
    validar_nome_branch,
)


def main():
    print("=" * 60)
    print("AULA 13 - GIT E GITHUB PARA PROJETOS DE DADOS")
    print("=" * 60)

    projeto = BASE / "projetos" / "churn_profissional"

    print("\n1. VALIDANDO NOME DE BRANCH")
    nome = "feature/preprocessamento"

    assert validar_nome_branch(nome)
    print("Nome valido:", nome)

    print("\n2. AUDITANDO ARQUIVOS LOCAIS")
    resultado = auditar_projeto(projeto)

    print(json.dumps(
        resultado,
        ensure_ascii=False,
        indent=2,
    ))

    print("\n3. SALVANDO RELATORIO")
    destino = (
        BASE
        / "resultados"
        / "aula13_auditoria_versionamento.json"
    )

    destino.write_text(
        json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    assert destino.is_file()
    assert resultado["total_arquivos"] > 0

    print("\nRelatorio:", destino.name)
    print("Nenhum comando Git foi executado.")
    print("AULA 13 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
