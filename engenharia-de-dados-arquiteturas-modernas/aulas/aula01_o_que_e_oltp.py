"""Laboratorio: demonstracao das transacoes OLTP."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.minishop_oltp import (
    ErroCompra,
    contar_registros,
    consultar_estoque,
    consultar_pedido,
    criar_banco,
    registrar_compra,
)


def main():
    banco = BASE / "dados" / "raw" / "minishop_aula01.db"
    relatorio = (
        BASE / "resultados" / "aula01_oltp_minishop.json"
    )

    print("===== MINISHOP - OLTP =====")

    criar_banco(banco)

    print("\nESTOQUE INICIAL")
    estoque_antes = consultar_estoque(banco, 1)
    print("Teclados:", estoque_antes)

    print("\nREGISTRANDO COMPRA")

    compra = registrar_compra(
        banco,
        cliente_id=1,
        itens=[(1, 1), (2, 2)],
    )

    print("Pedido:", compra["pedido_id"])
    print("Status:", compra["status"])
    print("Total em centavos:", compra["total_centavos"])
    print("Total em reais: R$", compra["total_centavos"] / 100)

    print("\nCONSULTA OPERACIONAL")

    pedido = consultar_pedido(banco, compra["pedido_id"])
    print("Pedido confirmado:", pedido)

    print("\nTESTANDO ATOMICIDADE")

    estoque_antes_falha = consultar_estoque(banco, 1)

    try:
        registrar_compra(
            banco,
            cliente_id=2,
            itens=[(1, 1)],
            pagamento_aprovado=False,
        )
    except ErroCompra as erro:
        print("Compra cancelada:", erro)

    estoque_depois_falha = consultar_estoque(banco, 1)

    assert estoque_depois_falha == estoque_antes_falha
    print("Rollback confirmado: estoque preservado")

    resultado = {
        "aula": 1,
        "tema": "OLTP",
        "banco": str(banco),
        "compra": compra,
        "pedido": {
            "id": pedido[0],
            "cliente_id": pedido[1],
            "total_centavos": pedido[2],
            "status": pedido[3],
        },
        "rollback_preservou_estoque": True,
        "registros": contar_registros(banco),
    }

    relatorio.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("\nREGISTROS DAS TABELAS")
    for tabela, quantidade in resultado["registros"].items():
        print(f"{tabela}: {quantidade}")

    print("\nRelatorio:", relatorio)
    print("AULA 01 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
