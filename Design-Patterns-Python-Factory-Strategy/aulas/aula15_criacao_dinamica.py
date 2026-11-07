"""Laboratorio da Aula 15 - Criacao dinamica."""

import argparse
import contextlib
import io
import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula15_criacao_dinamica import (
    TIPOS_DISPONIVEIS,
    MAPA_PEDIDOS,
    criar_pedido_condicional,
    criar_pedido_mapa,
    processar_pedido,
    escolher_por_input,
    analisar_criacao_dinamica,
)


def capturar(funcao):
    saida = io.StringIO()

    with contextlib.redirect_stdout(saida):
        resultado = funcao()

    return resultado, saida.getvalue().strip()


def main():
    parser = argparse.ArgumentParser(
        description="Aula 15 - Criacao dinamica"
    )

    parser.add_argument(
        "--interativo",
        action="store_true",
        help="Solicita o tipo de pagamento no terminal",
    )

    args = parser.parse_args()

    print("===== AULA 15 - CRIACAO DINAMICA =====")
    print("\n1. TIPOS DISPONIVEIS")
    print(TIPOS_DISPONIVEIS)

    print("\n2. SELECAO COM IF/ELIF")
    condicional = {}

    for tipo in TIPOS_DISPONIVEIS:
        pedido, mensagem = capturar(
            lambda t=tipo: processar_pedido(
                t, 200, "condicional"
            )
        )

        condicional[tipo] = {
            "factory": type(pedido).__name__,
            "mensagem": mensagem,
        }

        print(f"{tipo}: {mensagem}")

    print("\n3. SELECAO COM DICIONARIO")
    mapa = {}

    for tipo in TIPOS_DISPONIVEIS:
        pedido, mensagem = capturar(
            lambda t=tipo: processar_pedido(t, 100)
        )

        mapa[tipo] = {
            "factory": type(pedido).__name__,
            "mensagem": mensagem,
        }

        print(f"{tipo}: {mensagem}")

    print("\n4. MAPA DE FACTORIES")
    print({
        tipo: classe.__name__
        for tipo, classe in MAPA_PEDIDOS.items()
    })

    print("\n5. ENTRADA SIMULADA")
    pedido_input, mensagem_input = capturar(
        lambda: escolher_por_input(
            valor=150,
            entrada=lambda _: "pix",
        )
    )

    print("Escolha: pix")
    print(mensagem_input)

    print("\n6. TIPO INVALIDO")
    erro_capturado = False

    try:
        criar_pedido_mapa("transferencia")
    except ValueError as erro:
        erro_capturado = True
        print("Erro esperado:", erro)

    print("\n7. LIMITACAO")
    analise = analisar_criacao_dinamica()

    print(
        "Adicionar um novo pagamento exige "
        "atualizar MAPA_PEDIDOS:",
        analise[
            "mapa_precisa_ser_editado_para_novos_tipos"
        ],
    )

    if not erro_capturado:
        raise RuntimeError("Tipo invalido nao rejeitado")

    if set(mapa) != set(TIPOS_DISPONIVEIS):
        raise RuntimeError("Mapa incompleto")

    relatorio = {
        "aula": 15,
        "titulo": "Criacao dinamica",
        "condicional": condicional,
        "mapa": mapa,
        "entrada_simulada": {
            "tipo": "pix",
            "factory": type(pedido_input).__name__,
            "mensagem": mensagem_input,
        },
        "tipo_invalido_rejeitado": erro_capturado,
        "analise": analise,
    }

    destino = (
        BASE / "resultados"
        / "aula15_criacao_dinamica.json"
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
    print("AULA 15 EXECUTADA COM SUCESSO!")

    # Modo opcional, fora da validacao automatizada.
    if args.interativo:
        print("\n8. MODO INTERATIVO")
        escolher_por_input()


if __name__ == "__main__":
    main()
