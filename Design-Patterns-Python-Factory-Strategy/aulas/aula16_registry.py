"""Executa os exemplos da Aula 16 - Registry."""

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula16_registry import (
    Registry,
    construir_registro,
    finalizar_pagamento,
    PedidoTransferenciaFactory,
    demonstrar_registro_dinamico,
    demonstrar_substituicao,
    analisar_registry,
)


def capturar(funcao):
    saida = io.StringIO()

    with contextlib.redirect_stdout(saida):
        resultado = funcao()

    return resultado, saida.getvalue().strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interativo", action="store_true")
    args = parser.parse_args()

    print("===== AULA 16 - REGISTRY =====")

    registro = construir_registro()

    print("\n1. FACTORIES REGISTRADAS")

    print({
        chave: classe.__name__
        for chave, classe in registro.mapa.items()
    })

    print("\n2. CRIACAO DINAMICA DE PEDIDOS")

    resultados = {}

    for tipo in ("pix", "cartao", "boleto"):
        pedido, mensagem = capturar(
            lambda t=tipo: finalizar_pagamento(
                registro, t, 100
            )
        )

        resultados[tipo] = {
            "classe": type(pedido).__name__,
            "mensagem": mensagem,
        }

        print(f"{tipo}: {mensagem}")

    print("\n3. REGISTRO EM TEMPO DE EXECUCAO")

    registro.registrar(
        "transferencia",
        PedidoTransferenciaFactory,
    )

    pedido_novo, mensagem_nova = capturar(
        lambda: finalizar_pagamento(
            registro,
            "transferencia",
            200,
        )
    )

    print("Nova factory:", type(pedido_novo).__name__)
    print(mensagem_nova)

    print("\n4. TIPO NAO REGISTRADO")

    erro_capturado = False

    try:
        registro.criar("desconhecido")
    except ValueError as erro:
        erro_capturado = True
        print("Erro esperado:", erro)

    print("\n5. REGISTRO DUPLICADO")

    substituicao = demonstrar_substituicao()

    print(json.dumps(
        substituicao,
        indent=2,
        ensure_ascii=False,
    ))

    print("\n6. ANALISE DO PADRAO")

    analise = analisar_registry()
    dinamico = demonstrar_registro_dinamico()

    print(json.dumps(
        analise,
        indent=2,
        ensure_ascii=False,
    ))

    if not erro_capturado:
        raise RuntimeError("Chave invalida nao rejeitada")

    if not substituicao["sobrescreveu"]:
        raise RuntimeError("Substituicao nao demonstrada")

    if len(resultados) != 3:
        raise RuntimeError("Factories iniciais incompletas")

    relatorio = {
        "aula": 16,
        "titulo": "Registry",
        "pagamentos": resultados,
        "registro_dinamico": dinamico,
        "transferencia": {
            "classe": type(pedido_novo).__name__,
            "mensagem": mensagem_nova,
        },
        "tipo_invalido_rejeitado": erro_capturado,
        "substituicao": substituicao,
        "analise": analise,
    }

    destino = (
        BASE / "resultados"
        / "aula16_registry.json"
    )

    destino.parent.mkdir(parents=True, exist_ok=True)

    destino.write_text(
        json.dumps(
            relatorio,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nRELATORIO:", destino)
    print("AULA 16 EXECUTADA COM SUCESSO!")

    if args.interativo:
        print("\n7. MODO INTERATIVO")
        tipo = input("Tipo de pagamento: ")
        finalizar_pagamento(registro, tipo, 100)


if __name__ == "__main__":
    main()
