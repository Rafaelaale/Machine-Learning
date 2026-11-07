"""Laboratorio da Aula 13 - Simple Factory."""

import contextlib
import io
import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula13_simple_factory import (
    ServicoDeCartao,
    ServicoDePix,
    ServicoDePedidoComFuncao,
    ServicoDePedido,
    FabricaDePagamento,
    criar_servico_pagamento,
    analisar_simple_factory,
)


def capturar_pagamento(pedido, valor):
    saida = io.StringIO()

    with contextlib.redirect_stdout(saida):
        pedido.finalizar_pedido(valor)

    return saida.getvalue().strip()


def main():
    print("===== AULA 13 - SIMPLE FACTORY =====")

    print("\n1. FABRICA POR FUNCAO")

    pagamento_cartao = criar_servico_pagamento(
        "cartao"
    )
    pagamento_pix = criar_servico_pagamento("pix")

    print(
        "Cartao:",
        type(pagamento_cartao).__name__,
    )
    print(
        "PIX:",
        type(pagamento_pix).__name__,
    )

    print("\n2. PEDIDO COM FACTORY POR FUNCAO")

    pedido_funcao = ServicoDePedidoComFuncao("pix")

    mensagem_funcao = capturar_pagamento(
        pedido_funcao,
        200,
    )

    print(mensagem_funcao)

    print("\n3. FABRICA POR CLASSE")

    servico = FabricaDePagamento.criar("pix")

    print("Servico criado:", type(servico).__name__)

    print("\n4. PEDIDO COM CARTAO")

    pedido_cartao = ServicoDePedido("cartao")

    mensagem_cartao = capturar_pagamento(
        pedido_cartao,
        200,
    )

    print(mensagem_cartao)

    print("\n5. PEDIDO COM PIX")

    pedido_pix = ServicoDePedido("pix")

    mensagem_pix = capturar_pagamento(
        pedido_pix,
        200,
    )

    print(mensagem_pix)

    print("\n6. FACTORY REUTILIZAVEL")

    pedido_extra = ServicoDePedido("pix")

    mensagem_extra = capturar_pagamento(
        pedido_extra,
        150,
    )

    print(mensagem_extra)

    print("\n7. VALIDANDO TIPO INVALIDO")

    erro_capturado = False

    try:
        FabricaDePagamento.criar("boleto")
    except ValueError as erro:
        erro_capturado = True
        print("Erro esperado:", erro)

    print("\n8. BENEFICIOS E LIMITACOES")

    analise = analisar_simple_factory()

    print(json.dumps(
        analise,
        indent=2,
        ensure_ascii=False,
    ))

    if not isinstance(pagamento_cartao, ServicoDeCartao):
        raise RuntimeError(
            "A fabrica por funcao criou o tipo incorreto"
        )

    if not isinstance(pagamento_pix, ServicoDePix):
        raise RuntimeError(
            "A fabrica por funcao criou o tipo incorreto"
        )

    if mensagem_funcao != (
        "Pagamento via PIX de R$ 200 processado."
    ):
        raise RuntimeError(
            "Falha no pedido com factory por funcao"
        )

    if mensagem_cartao != (
        "Pagamento de R$ 200 processado."
    ):
        raise RuntimeError("Falha no cartao")

    if mensagem_pix != (
        "Pagamento via PIX de R$ 200 processado."
    ):
        raise RuntimeError("Falha no PIX")

    if mensagem_extra != (
        "Pagamento via PIX de R$ 150 processado."
    ):
        raise RuntimeError("Falha no pedido adicional")

    if not erro_capturado:
        raise RuntimeError(
            "Tipo de pagamento invalido nao rejeitado"
        )

    relatorio = {
        "aula": 13,
        "titulo": "Simple Factory",
        "factory_funcao": {
            "cartao": type(pagamento_cartao).__name__,
            "pix": type(pagamento_pix).__name__,
            "mensagem_pedido": mensagem_funcao,
        },
        "factory_classe": {
            "cartao": mensagem_cartao,
            "pix": mensagem_pix,
            "pix_150": mensagem_extra,
        },
        "erro_tipo_invalido": erro_capturado,
        "analise": analise,
    }

    destino = (
        BASE / "resultados"
        / "aula13_simple_factory.json"
    )

    destino.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destino.write_text(
        json.dumps(
            relatorio,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nRELATORIO:", destino)
    print("AULA 13 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
