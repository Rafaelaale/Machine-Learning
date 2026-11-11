import json
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
RESULTADOS = BASE / "resultados"
RESULTADOS.mkdir(exist_ok=True)

CATALOGO = "prod"
ESQUEMA = "prod.gold"
TABELA = "prod.gold.escoragem_propensao_compra"

# Simulador didatico de grants.
# Nao representa toda a semantica do Unity Catalog.
# Nao conecta a nenhum servico remoto.

grants = {}


def conceder(tipo, objeto, principal, *privilegios):
    grants.setdefault(
        (tipo, objeto, principal), set()
    ).update(privilegios)


def revogar(tipo, objeto, principal, *privilegios):
    grants.get(
        (tipo, objeto, principal), set()
    ).difference_update(privilegios)


def possui(principal, privilegio, nivel):
    hierarquia = [
        ("catalog", CATALOGO)
    ]

    if nivel in ("schema", "table"):
        hierarquia.append(("schema", ESQUEMA))

    if nivel == "table":
        hierarquia.append(("table", TABELA))

    return any(
        privilegio in grants.get(
            (tipo, objeto, principal), set()
        )
        for tipo, objeto in hierarquia
    )


def pode_ler(principal):
    return (
        possui(principal, "USE CATALOG", "catalog")
        and possui(principal, "USE SCHEMA", "schema")
        and possui(principal, "SELECT", "table")
    )


def pode_escrever(principal):
    return (
        possui(principal, "USE CATALOG", "catalog")
        and possui(principal, "USE SCHEMA", "schema")
        and possui(principal, "MODIFY", "table")
    )


def pode_criar_tabela(principal):
    return (
        possui(principal, "USE CATALOG", "catalog")
        and possui(principal, "USE SCHEMA", "schema")
        and possui(principal, "CREATE TABLE", "schema")
    )


resultados = []


def teste(descricao, condicao):
    if not condicao:
        raise AssertionError(descricao)

    resultados.append(descricao)
    print("OK:", descricao)


print("===== SIMULANDO ACESSOS DE ANALISTAS =====")

conceder(
    "catalog", CATALOGO, "analistas",
    "USE CATALOG"
)

conceder(
    "schema", ESQUEMA, "analistas",
    "USE SCHEMA"
)

conceder(
    "table", TABELA, "analistas",
    "SELECT", "MODIFY"
)

teste(
    "Leitura inicialmente autorizada",
    pode_ler("analistas")
)

teste(
    "Escrita inicialmente autorizada",
    pode_escrever("analistas")
)

revogar(
    "table", TABELA, "analistas",
    "MODIFY"
)

teste(
    "REVOKE MODIFY bloqueia escrita e preserva leitura",
    not pode_escrever("analistas")
    and pode_ler("analistas")
)

teste(
    "Analistas nao podem criar tabelas",
    not pode_criar_tabela("analistas")
)


print("===== SIMULANDO HERANCA DE PRIVILEGIOS =====")

conceder(
    "catalog", CATALOGO, "grupo_heranca",
    "USE CATALOG"
)

conceder(
    "schema", ESQUEMA, "grupo_heranca",
    "USE SCHEMA", "SELECT"
)

conceder(
    "table", TABELA, "grupo_heranca",
    "SELECT"
)

revogar(
    "table", TABELA, "grupo_heranca",
    "SELECT"
)

teste(
    "SELECT herdado continua apos REVOKE na tabela",
    pode_ler("grupo_heranca")
)

revogar(
    "schema", ESQUEMA, "grupo_heranca",
    "SELECT"
)

teste(
    "Remover grant do schema elimina leitura neste exemplo",
    not pode_ler("grupo_heranca")
)


print("===== SIMULANDO IDENTIDADE DE PIPELINE =====")

conceder(
    "catalog", CATALOGO, "svc_pipeline_prod",
    "USE CATALOG"
)

conceder(
    "schema", ESQUEMA, "svc_pipeline_prod",
    "USE SCHEMA", "CREATE TABLE"
)

conceder(
    "table", TABELA, "svc_pipeline_prod",
    "SELECT", "MODIFY"
)

teste(
    "Pipeline autorizada a modificar dados",
    pode_escrever("svc_pipeline_prod")
)

teste(
    "Pipeline autorizada a criar tabelas",
    pode_criar_tabela("svc_pipeline_prod")
)


relatorio = {
    "aula": "Aula 6.5 - Gerenciamento de Acessos Unity Catalog",
    "data_utc": datetime.now(timezone.utc).isoformat(),
    "validacoes": len(resultados),
    "resultados": resultados,
    "ambiente": "simulacao_didatica_local",
    "databricks_conectado": False,
    "revoke_remoto_executado": False,
    "notas": [
        "Modelo simplificado de permissoes.",
        "Nao modela ownership, grupos aninhados ou todas as regras.",
        "Nao modifica catalogos, usuarios ou grants reais."
    ]
}

destino = RESULTADOS / "AUDITORIA_UNITY_CATALOG.json"

destino.write_text(
    json.dumps(
        relatorio,
        indent=2,
        ensure_ascii=False
    ),
    encoding="utf-8"
)

print("TESTES DE ACESSO: 8/8 APROVADOS")
print("UNITY CATALOG REMOTO: NAO ALTERADO")