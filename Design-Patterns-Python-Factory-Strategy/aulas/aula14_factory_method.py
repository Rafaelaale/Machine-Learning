"""Laboratorio da Aula 14 - Factory Method."""

import contextlib
import io
import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula14_factory_method import (
    ServicoDePedidoFactory,
    PedidoCartaoFactory,
    PedidoPixFactory,
    PedidoBoletoFactory,
    analisar_factory_method,
)


def capturar(pedido, valor):
    saida = io.StringIO()

    with contextlib.redirect_stdout(saida):
        pedido.finalizar_pedido(valor)

    return saida.getvalue().strip()


def main():
    print("===== AULA 14 - FACTORY METHOD =====")

    print("\n1. FACTORY ABSTRATA")
    print(
        "Criador abstrato:",
        ServicoDePedidoFactory.__name__,
    )
    print(
        "Metodo abstrato:",
        "criar_pagamento",
    )

    print("\n2. PAGAMENTO PIX")
    pedido_pix = PedidoPixFactory()
    mensagem_pix = capturar(pedido_pix, 250)
    print(mensagem_pix)

    print("\n3. PAGAMENTO CARTAO")
    pedido_cartao = PedidoCartaoFactory()
    mensagem_cartao = capturar(pedido_cartao, 180)
    print(mensagem_cartao)

    print("\n4. EXTENSAO: BOLETO")
    pedido_boleto = PedidoBoletoFactory()
    mensagem_boleto = capturar(pedido_boleto, 120)
    print(mensagem_boleto)

    print("\n5. TIPO DE OBJETO CRIADO")
    print(
        "PIX:",
        type(pedido_pix.criar_pagamento()).__name__,
    )
    print(
        "Cartao:",
        type(pedido_cartao.criar_pagamento()).__name__,
    )
    print(
        "Boleto:",
        type(pedido_boleto.criar_pagamento()).__name__,
    )

    print("\n6. BENEFICIOS E LIMITACOES")
    analise = analisar_factory_method()

    print(json.dumps(
        analise,
        indent=2,
        ensure_ascii=False,
    ))

    if mensagem_pix != (
        "Pagamento via PIX de R$ 250 processado."
    ):
        raise RuntimeError("Falha no pagamento PIX")

    if mensagem_cartao != (
        "Pagamento no cartão de R$ 180 processado."
    ):
        raise RuntimeError("Falha no pagamento com cartao")

    if mensagem_boleto != (
        "Pagamento via boleto de R$ 120 processado."
    ):
        raise RuntimeError("Falha na extensao por boleto")

    relatorio = {
        "aula": 14,
        "titulo": "Factory Method",
        "pagamentos": {
            "pix": mensagem_pix,
            "cartao": mensagem_cartao,
            "boleto": mensagem_boleto,
        },
        "analise": analise,
    }

    destino = (
        BASE / "resultados"
        / "aula14_factory_method.json"
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
    print("AULA 14 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
