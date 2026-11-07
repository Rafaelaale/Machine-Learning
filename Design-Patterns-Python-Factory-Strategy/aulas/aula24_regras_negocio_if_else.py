"""Laboratorio da Aula 24 - Regras de negocio if/else."""

import json
import sys
from pathlib import Path


RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.aula24_regras_negocio_if_else import (
    Cliente,
    calcular_preco_inicial,
    calcular_preco,
    analisar_aula24,
)


def main():
    print("===== AULA 24 - REGRAS DE NEGOCIO IF/ELSE =====")

    clientes = [
        Cliente("Ana", "vip"),
        Cliente("Bruno", "novo"),
        Cliente("Carla", "funcionario"),
        Cliente("Diego", "comum"),
        Cliente("Eva", "parceria"),
        Cliente("Fabio", "parceria", "empresa_x"),
        Cliente("Gabi", "parceria", "empresa_y"),
        Cliente("Helena", "black_friday"),
    ]

    print("\n1. FUNCAO INICIAL - TOTAL R$ 100")

    iniciais = []

    for cliente in clientes[:4]:
        preco = calcular_preco_inicial(cliente, 100)
        iniciais.append({
            "cliente": cliente.nome,
            "tipo": cliente.tipo,
            "total": 100,
            "preco": preco,
        })

        print(f"{cliente.tipo}: R$ {preco:.2f}")

    print("\n2. FUNCAO EXPANDIDA - TOTAL R$ 100")

    expandidos = []

    for cliente in clientes:
        preco = calcular_preco(cliente, 100)
        expandidos.append({
            "cliente": cliente.nome,
            "tipo": cliente.tipo,
            "parceiro": cliente.parceiro,
            "total": 100,
            "preco": preco,
        })

        print(
            f"{cliente.nome} ({cliente.tipo}, "
            f"parceiro={cliente.parceiro}): R$ {preco:.2f}"
        )

    print("\n3. BLACK FRIDAY E LIMITE DE R$ 500")

    black_friday = Cliente("Helena", "black_friday")

    limites = []

    for total in (400, 500, 600):
        preco = calcular_preco(black_friday, total)
        limites.append({
            "total": total,
            "preco": preco,
        })

        print(
            f"Compra R$ {total:.2f} -> "
            f"Preco R$ {preco:.2f}"
        )

    print("\n4. CODE SMELLS IDENTIFICADOS")

    analise = analisar_aula24()

    for indice, problema in enumerate(
        analise["code_smells"], start=1
    ):
        print(f"{indice}. {problema}")

    print("\n5. PROPOSTA DA PROXIMA AULA")

    print(analise["solucao_proposta"])

    if [item["preco"] for item in iniciais] != [
        80.0, 90.0, 70.0, 100
    ]:
        raise RuntimeError("Regras iniciais incorretas")

    if [item["preco"] for item in expandidos] != [
        80.0, 90.0, 70.0, 100, 85.0, 75.0, 80.0, 50.0
    ]:
        raise RuntimeError("Regras expandidas incorretas")

    if [item["preco"] for item in limites] != [
        200.0, 250.0, 270.0
    ]:
        raise RuntimeError("Limites Black Friday incorretos")

    if analise["strategy_implementado"]:
        raise RuntimeError("Nao antecipar a proxima aula")

    relatorio = {
        "aula": 24,
        "titulo": analise["titulo"],
        "precos_iniciais": iniciais,
        "precos_expandidos": expandidos,
        "limites_black_friday": limites,
        "analise": analise,
    }

    destino = (
        RAIZ / "resultados"
        / "aula24_regras_negocio_if_else.json"
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
    print("AULA 24 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
