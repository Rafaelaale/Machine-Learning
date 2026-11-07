"""Aula 04 - Modelo conceitual da Minishop.

Catalogo de entidades, atributos e relacionamentos.
Nao modifica os bancos existentes.
"""

from dataclasses import dataclass, asdict


@dataclass(frozen=True)
class Entidade:
    nome: str
    atributos: tuple[str, ...]


@dataclass(frozen=True)
class Relacionamento:
    origem: str
    verbo: str
    destino: str
    por_origem: str
    por_destino: str
    observacao: str = ""


ENTIDADES = (
    Entidade("cliente", ("id", "nome", "email")),
    Entidade(
        "pedido",
        ("id", "cliente_id", "data", "estado", "valor"),
    ),
    Entidade(
        "item_pedido",
        ("id", "pedido_id", "produto_id", "quantidade", "preco"),
    ),
    Entidade(
        "produto",
        ("id", "nome", "preco", "categoria_id"),
    ),
    Entidade("categoria", ("id", "nome")),
    Entidade(
        "inventario",
        ("produto_id", "quantidade_disponivel"),
    ),
    Entidade(
        "movimento_inventario",
        ("id", "item_id", "produto_id", "quantidade", "tipo"),
    ),
    Entidade(
        "fatura",
        ("id", "pedido_id", "valor", "estado"),
    ),
    Entidade(
        "pagamento",
        ("id", "pedido_id", "valor", "estado"),
    ),
)


# por_origem: quantos registros DESTINO por um ORIGEM.
# por_destino: quantos registros ORIGEM por um DESTINO.
#
# Cardinalidades sao hipoteses para validacao de negocio.
RELACIONAMENTOS = (
    Relacionamento(
        "cliente", "faz", "pedido", "0..N", "1",
        "Cliente cadastrado pode ainda nao ter comprado.",
    ),
    Relacionamento(
        "pedido", "contem", "item_pedido", "1..N", "1",
        "Pedido finalizado possui pelo menos um item.",
    ),
    Relacionamento(
        "item_pedido", "referencia", "produto", "1", "0..N",
    ),
    Relacionamento(
        "categoria", "organiza", "produto", "0..N", "1",
        "Categoria pode existir sem produtos.",
    ),
    Relacionamento(
        "produto", "possui", "inventario", "1", "1",
        "Hipotese de um estoque por produto.",
    ),
    Relacionamento(
        "item_pedido", "gera", "movimento_inventario", "0..1", "1",
        "Apos confirmacao: exatamente uma saida por item.",
    ),
    Relacionamento(
        "pedido", "gera", "fatura", "0..1", "1",
        "Pedido pendente pode ainda nao ter fatura.",
    ),
    Relacionamento(
        "pedido", "possui", "pagamento", "0..1", "1",
        "Escopo atual: um registro de pagamento por pedido.",
    ),
)


REGRAS = {
    "REGRA_01": "Um pedido pertence a exatamente um cliente.",
    "REGRA_02": "Cada item pertence a um unico pedido.",
    "REGRA_03": "Cada item referencia um unico produto.",
    "REGRA_04": "Cada produto pertence a uma categoria.",
    "REGRA_05": "Nao permitir estoque negativo.",
    "REGRA_06": "Uma venda confirmada gera baixa de estoque.",
    "REGRA_07": "Uma compra nao deve ser confirmada sem pagamento aprovado.",
    "REGRA_08": "No escopo atual, cada pedido gera no maximo uma fatura.",
}


PENDENCIAS = (
    "Confirmar se cliente sem pedido e permitido.",
    "Confirmar se pedidos pendentes podem ter zero itens.",
    "Definir quando a fatura e emitida.",
    "Confirmar tratamento de pagamentos recusados e tentativas.",
    "Confirmar se ha varios depositos por produto.",
    "Confirmar se ha devolucoes e movimentos de entrada.",
    "Confirmar dados obrigatorios e regras fiscais da fatura.",
)


def validar_modelo():
    """Verifica a integridade estrutural do catalogo."""
    erros = []
    nomes = [e.nome for e in ENTIDADES]

    if len(nomes) != len(set(nomes)):
        erros.append("Entidades duplicadas")

    for entidade in ENTIDADES:
        if not entidade.atributos:
            erros.append(f"Sem atributos: {entidade.nome}")

        if len(entidade.atributos) != len(set(entidade.atributos)):
            erros.append(f"Atributos duplicados: {entidade.nome}")

    cardinalidades = {"1", "0..1", "1..N", "0..N"}

    for relacao in RELACIONAMENTOS:
        if relacao.origem not in nomes:
            erros.append(f"Origem inexistente: {relacao.origem}")

        if relacao.destino not in nomes:
            erros.append(f"Destino inexistente: {relacao.destino}")

        if relacao.por_origem not in cardinalidades:
            erros.append("Cardinalidade de origem invalida")

        if relacao.por_destino not in cardinalidades:
            erros.append("Cardinalidade de destino invalida")

    return erros


def obter_entidade(nome):
    """Busca uma entidade no catalogo."""
    for entidade in ENTIDADES:
        if entidade.nome == nome:
            return entidade

    raise KeyError(f"Entidade desconhecida: {nome}")


def relacionamentos_de(nome):
    """Lista relacoes em que uma entidade participa."""
    obter_entidade(nome)

    return [
        relacao
        for relacao in RELACIONAMENTOS
        if nome in (relacao.origem, relacao.destino)
    ]


def exportar_catalogo():
    """Gera representacao estruturada do modelo."""
    return {
        "modelo": "Entidade-Relacionamento conceitual",
        "entidades": [asdict(e) for e in ENTIDADES],
        "relacionamentos": [
            asdict(r) for r in RELACIONAMENTOS
        ],
        "regras_negocio": REGRAS,
        "pendencias_validacao": list(PENDENCIAS),
        "modelo_aprovado_pelo_usuario": False,
    }
