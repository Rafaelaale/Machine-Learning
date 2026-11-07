"""Executa os exemplos da Aula 12."""

import contextlib
import io
import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula12_criacao_objetos import (
    ServicoDePedidoRigido,
    ServicoDePedido,
    ServicoDePagamento,
    ServicoDePix,
    analisar_acoplamento,
)


def capturar_pagamento(pedido, valor):
    saida = io.StringIO()

    with contextlib.redirect_stdout(saida):
        pedido.finalizar_pedido(valor)

    return saida.getvalue().strip()


def main():
    print("===== AULA 12 - CRIANDO OBJETOS DO JEITO ERRADO =====")

    print("\n1. SERVICO DE PEDIDO RIGIDO")

    rigido = ServicoDePedidoRigido()
    mensagem_rigida = capturar_pagamento(rigido, 120)

    print("Servico:", type(rigido.pagamento).__name__)
    print(mensagem_rigida)

    print("\n2. SERVICO DE PEDIDO COM CARTAO")

    cartao = ServicoDePedido("cartao")
    mensagem_cartao = capturar_pagamento(cartao, 120)

    print("Servico:", type(cartao.pagamento).__name__)
    print(mensagem_cartao)

    print("\n3. SERVICO DE PEDIDO COM PIX")

    pix = ServicoDePedido("pix")
    mensagem_pix = capturar_pagamento(pix, 120)

    print("Servico:", type(pix.pagamento).__name__)
    print(mensagem_pix)

    print("\n4. TIPO DE PAGAMENTO PADRAO")

    padrao = ServicoDePedido()

    print("Tipo:", padrao.tipo_pagamento)
    print("Servico:", type(padrao.pagamento).__name__)

    print("\n5. TRATAMENTO DE TIPO INVALIDO")

    erro_capturado = False

    try:
        ServicoDePedido("boleto")
    except ValueError as erro:
        erro_capturado = True
        print("Erro esperado:", erro)

    print("\n6. ANALISE DE ACOPLAMENTO")

    analise = analisar_acoplamento()

    print(json.dumps(
        analise,
        ensure_ascii=False,
        indent=2,
    ))

    if mensagem_rigida != "Pagamento de R$ 120 processado.":
        raise RuntimeError("Falha no pagamento rigido")

    if mensagem_cartao != "Pagamento de R$ 120 processado.":
        raise RuntimeError("Falha no pagamento com cartao")

    if mensagem_pix != "Pagamento via PIX de R$ 120 processado.":
        raise RuntimeError("Falha no pagamento PIX")

    if not erro_capturado:
        raise RuntimeError("Tipo invalido nao foi rejeitado")

    if not isinstance(rigido.pagamento, ServicoDePagamento):
        raise RuntimeError("Servico rigido incorreto")

    if not isinstance(pix.pagamento, ServicoDePix):
        raise RuntimeError("Servico PIX incorreto")

    relatorio = {
        "aula": 12,
        "titulo": "Criando objetos do jeito errado",
        "criacao_rigida": {
            "servico": type(rigido.pagamento).__name__,
            "mensagem": mensagem_rigida,
        },
        "cartao": {
            "servico": type(cartao.pagamento).__name__,
            "mensagem": mensagem_cartao,
        },
        "pix": {
            "servico": type(pix.pagamento).__name__,
            "mensagem": mensagem_pix,
        },
        "tipo_padrao": padrao.tipo_pagamento,
        "erro_tipo_invalido": erro_capturado,
        "analise": analise,
    }

    destino = (
        BASE / "resultados"
        / "aula12_criacao_objetos.json"
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
    print("AULA 12 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
