"""Laboratorio da Aula 25 - Padrao Strategy."""

import json
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula25_padrao_strategy import (
    RegraDeDesconto,
    DescontoVip,
    DescontoNovo,
    DescontoFuncionario,
    SemDesconto,
    Cliente,
    calcular_preco,
    criar_clientes_exemplo,
    demonstrar_troca_estrategia,
    demonstrar_extensibilidade,
    analisar_aula25,
)


def main():
    print("===== AULA 25 - PADRAO STRATEGY =====")

    print("\n1. ESTRATEGIAS INDEPENDENTES")

    estrategias = [
        DescontoVip(),
        DescontoNovo(),
        DescontoFuncionario(),
        SemDesconto(),
    ]

    resultados_estrategias = []

    for estrategia in estrategias:
        preco = estrategia.calcular(200)

        resultados_estrategias.append({
            "estrategia": type(estrategia).__name__,
            "total": 200,
            "preco": preco,
        })

        print(
            f"{type(estrategia).__name__}: "
            f"R$ {preco:.2f}"
        )

    print("\n2. CLIENTES DA TRANSCRICAO")

    clientes = criar_clientes_exemplo()
    resultados_clientes = []

    for chave, cliente in clientes.items():
        preco = calcular_preco(cliente, 200)

        resultados_clientes.append({
            "chave": chave,
            "nome": cliente.nome,
            "estrategia": type(
                cliente.regra_de_desconto
            ).__name__,
            "total": 200,
            "preco": preco,
        })

        print(
            f"{cliente.nome}: R$ {preco:.2f} "
            f"({type(cliente.regra_de_desconto).__name__})"
        )

    print("\n3. TROCANDO A ESTRATEGIA DA MARIA")

    troca = demonstrar_troca_estrategia()

    print(
        "Com VIP:",
        f"R$ {troca['preco_com_vip']:.2f}",
    )
    print(
        "Com Novo:",
        f"R$ {troca['preco_com_novo']:.2f}",
    )

    print("\n4. PRINCIPIO ABERTO/FECHADO")

    extensibilidade = demonstrar_extensibilidade()

    print(
        "Nova estrategia:",
        extensibilidade["estrategia"],
    )
    print(
        "Preco final:",
        f"R$ {extensibilidade['preco_final']:.2f}",
    )

    print("\n5. ANALISE DO PADRAO")

    analise = analisar_aula25()

    print(json.dumps(
        analise,
        ensure_ascii=False,
        indent=2,
    ))

    esperados = [160.0, 180.0, 140.0, 200]
    obtidos = [
        item["preco"]
        for item in resultados_estrategias
    ]

    if obtidos != esperados:
        raise RuntimeError("Estratégias de desconto incorretas")

    if [item["preco"] for item in resultados_clientes] != [160.0, 180.0, 200, 140.0]:
        raise RuntimeError("Preços dos clientes incorretos")

    if troca["preco_com_vip"] != 160:
        raise RuntimeError("Falha na estrategia VIP")

    if troca["preco_com_novo"] != 180:
        raise RuntimeError("Falha na troca de estrategia")

    if extensibilidade["preco_final"] != 120:
        raise RuntimeError("Falha na nova estrategia")

    if analise["strategy_com_funcoes"]:
        raise RuntimeError("Nao antecipar a proxima aula")

    relatorio = {
        "aula": 25,
        "titulo": analise["titulo"],
        "estrategias": resultados_estrategias,
        "clientes": resultados_clientes,
        "troca_de_estrategia": troca,
        "extensibilidade": extensibilidade,
        "analise": analise,
    }

    destino = (
        RAIZ / "resultados"
        / "aula25_padrao_strategy.json"
    )

    destino.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destino.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\nRELATORIO:", destino)
    print("AULA 25 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
