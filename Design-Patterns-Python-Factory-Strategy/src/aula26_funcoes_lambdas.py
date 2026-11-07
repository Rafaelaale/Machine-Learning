"""Aula 26 - Funcoes de primeira classe e lambdas.

Implementacao de Strategy com funcoes, sem classes
abstratas e sem necessidade de objetos de estrategia.

IMPORTANTE:
A formula black_friday segue literalmente a transcricao:
total * 0.5 if total <= 500 else total * 0.9.

Logo, para total=600, a formula retorna 540, embora
o texto da transcricao indique 270.
"""


def desconto_vip(total):
    return total * 0.8


def desconto_novo(total):
    return total * 0.9


def desconto_funcionario(total):
    return total * 0.7


def sem_desconto(total):
    return total


def calcular_preco(total, estrategia):
    """Executa a estrategia recebida como argumento."""
    return estrategia(total)


# Exemplos de lambdas apresentados na transcricao.

soma = lambda a, b: a + b

desconto_estudante = lambda total: total * 0.85

black_friday = (
    lambda total: total * 0.5
    if total <= 500
    else total * 0.9
)

parceria_empresa_x = lambda total: total * 0.85 - 10

parceria_empresa_y = lambda total: total * 0.85 - 5


# Funcoes tambem podem ser armazenadas em colecoes.

ESTRATEGIAS = {
    "vip": desconto_vip,
    "novo": desconto_novo,
    "funcionario": desconto_funcionario,
    "sem_desconto": sem_desconto,
    "estudante": desconto_estudante,
    "black_friday": black_friday,
    "empresa_x": parceria_empresa_x,
    "empresa_y": parceria_empresa_y,
}


def demonstrar_primeira_classe():
    """Funcoes armazenadas, passadas e substituidas."""

    estrategia = desconto_vip
    preco_vip = calcular_preco(200, estrategia)

    estrategia = desconto_novo
    preco_novo = calcular_preco(200, estrategia)

    estrategias_lista = [
        desconto_vip,
        desconto_novo,
        sem_desconto,
    ]

    precos_lista = [
        calcular_preco(200, funcao)
        for funcao in estrategias_lista
    ]

    precos_dicionario = {
        nome: calcular_preco(200, ESTRATEGIAS[nome])
        for nome in ("vip", "novo", "estudante")
    }

    return {
        "preco_vip": preco_vip,
        "preco_novo": preco_novo,
        "precos_lista": precos_lista,
        "precos_dicionario": precos_dicionario,
    }


def criar_estrategia_percentual(fator):
    """Exemplo adicional: retornar uma funcao."""

    def estrategia(total):
        return total * fator

    return estrategia


def demonstrar_lambda_direta():
    """Passa uma lambda diretamente para calcular_preco."""

    return calcular_preco(
        300,
        lambda total: total * 0.75,
    )


def demonstrar_divergencia_black_friday():
    """Compara a formula literal ao resultado citado."""

    total = 600
    resultado_formula = calcular_preco(total, black_friday)
    resultado_citado = 270.0

    return {
        "total": total,
        "resultado_formula_transcrita": resultado_formula,
        "resultado_citado_na_transcricao": resultado_citado,
        "valores_coincidem": (
            resultado_formula == resultado_citado
        ),
        "formula_da_aula_24_para_600": (
            total * 0.5 * 0.9
        ),
    }


def analisar_aula26():
    return {
        "aula": 26,
        "titulo": "Aproveitando funcoes de primeira classe e lambdas",
        "padrao": "Strategy",
        "usa_classes_de_estrategia": False,
        "funcoes_primeira_classe": True,
        "lambda": True,
        "troca_dinamica": True,
        "funcoes_em_colecoes": True,
        "funcoes_retornadas_por_funcoes": True,
        "black_friday_formula_literal": True,
        "black_friday_600_formula": 540.0,
        "black_friday_600_texto": 270.0,
        "proximo_tema": "Template Method",
    }
