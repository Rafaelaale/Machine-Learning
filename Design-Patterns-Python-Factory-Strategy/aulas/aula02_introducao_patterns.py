"""Laboratorio pratico da Aula 02."""

import json
import sys
from pathlib import Path


BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula02_introducao_patterns import (
    CATEGORIAS,
    criar_notificacao,
    MensagemFormatada,
    MensagemComPrefixo,
    aplicar_comportamento,
    aplicar_desconto,
    aplicar_acrescimo,
)


def executar():
    print("===== AULA 02 - INTRODUCAO AOS DESIGN PATTERNS =====")

    print("\n1. CATEGORIAS DE PADROES")

    for categoria, dados in CATEGORIAS.items():
        print(
            categoria.upper(),
            "-",
            dados["objetivo"],
        )

    print("\n2. EXEMPLO CRIACIONAL")

    notificacao = criar_notificacao(
        "cliente@exemplo.com",
        "Pedido aprovado",
        "email",
    )

    print(notificacao.descrever())

    print("\n3. EXEMPLO ESTRUTURAL")

    mensagem = MensagemFormatada(
        "Pagamento confirmado"
    )

    mensagem_formatada = MensagemComPrefixo(
        mensagem,
        "[MINISHOP] ",
    )

    print("Original:", mensagem.renderizar())
    print("Composta:", mensagem_formatada.renderizar())

    print("\n4. EXEMPLO COMPORTAMENTAL")

    preco = 100.0

    desconto = aplicar_comportamento(
        preco, aplicar_desconto
    )

    acrescimo = aplicar_comportamento(
        preco, aplicar_acrescimo
    )

    print("Preco original:", preco)
    print("Com desconto:", desconto)
    print("Com acrescimo:", acrescimo)

    print("\n5. CONCLUSAO")

    print(
        "Padroes ajudam quando existe um problema "
        "recorrente de design."
    )

    print(
        "Evite acrescentar abstracoes "
        "sem uma necessidade concreta."
    )

    resultado = {
        "aula": 2,
        "assunto": "Introducao aos Design Patterns",
        "categorias": list(CATEGORIAS),
        "notificacao": notificacao.descrever(),
        "mensagem_original": mensagem.renderizar(),
        "mensagem_composta": mensagem_formatada.renderizar(),
        "preco_original": preco,
        "preco_com_desconto": desconto,
        "preco_com_acrescimo": acrescimo,
    }

    destino = (
        BASE / "resultados"
        / "aula02_introducao_patterns.json"
    )

    destino.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    destino.write_text(
        json.dumps(
            resultado,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nRELATORIO:", destino)
    print("AULA 02 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    executar()
