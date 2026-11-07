"""Executa e documenta a Aula 13."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula13_slowly_changing_dimensions import (
    CLIENTE,
    buscar_sk_atual,
    conectar,
    buscar_sk_historica,
    executar_exemplo,
)


def main():
    banco = (
        BASE / "dados" / "processed"
        / "minishop_scd_aula13.db"
    )

    print("===== AULA 13 - SLOWLY CHANGING DIMENSIONS =====")

    resultado = executar_exemplo(banco)

    print("\n1. DIMENSAO SCD TIPO 1")
    print(resultado["scd1"])

    print("\n2. DIMENSAO SCD TIPO 2")
    print(resultado["scd2"])

    print("\n3. VERSOES HISTORICAS")
    print(json.dumps(
        resultado["versoes"],
        indent=2,
        ensure_ascii=False,
    ))

    print("\n4. LOOKUP RETROATIVO")

    from contextlib import closing

    with closing(conectar(banco)) as conexao:
        retro = buscar_sk_historica(
            conexao, CLIENTE, "2023-12-15"
        )
        maio = buscar_sk_historica(
            conexao, CLIENTE, "2024-05-15"
        )

    atual = buscar_sk_atual(banco, CLIENTE)

    print("SK dezembro/2023:", retro)
    print("SK maio/2024:", maio)
    print("SK atual:", atual)

    assert resultado["scd2"] == {
        "Niteroi": 5000,
        "Santos": 1500,
    }
    assert resultado["scd1"] == {"Santos": 6500}
    assert retro != atual
    assert maio == atual
    assert resultado["vigencias_validas"]

    resultado["lookup"] = {
        "retroativo": retro,
        "maio": maio,
        "atual": atual,
    }

    arquivo = (
        BASE / "resultados"
        / "aula13_slowly_changing_dimensions.json"
    )

    arquivo.write_text(
        json.dumps(
            resultado, indent=2, ensure_ascii=False
        ),
        encoding="utf-8",
    )

    print("\n5. VALIDACAO")
    print("Vigencias sem sobreposicoes: True")
    print("Faturamento reconciliado: R$ 65,00")
    print("Relatorio:", arquivo)
    print("AULA 13 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
