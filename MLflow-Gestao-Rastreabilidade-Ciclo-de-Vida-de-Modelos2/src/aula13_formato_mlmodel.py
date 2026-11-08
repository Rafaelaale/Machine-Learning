"""Aula 13 - Inspecao do pacote MLmodel.

Consulta a versao production existente.
Inspeciona flavors, signature, ambiente,
input example e valida entradas.

Nao treina, registra, promove ou altera modelos.
"""

import hashlib
import json
import shutil
import warnings
from pathlib import Path

import mlflow
import mlflow.artifacts
import mlflow.pyfunc
import mlflow.sklearn
import numpy as np
import pandas as pd
import yaml

from mlflow.models import get_model_info

from src.aula04_primeira_run_mlflow import (
    RAIZ,
    carregar_dados,
)
from src.aula11_model_registry import (
    REGISTERED_MODEL_NAME,
    configurar_registry,
)
from src.aula12_promovendo_modelos import (
    novo_cliente,
)


MODEL_URI = (
    f"models:/{REGISTERED_MODEL_NAME}@production"
)

PASTA = RAIZ / "resultados" / "aula13_mlmodel"

JSON_RESULTADO = (
    RAIZ / "resultados" / "aula13_formato_mlmodel.json"
)

CSV_PREVISOES = PASTA / "previsoes_flavors.csv"
JSON_INVENTARIO = PASTA / "inventario_pacote.json"
JSON_CONTRATO = PASTA / "contrato_modelo.json"
JSON_CENARIOS = PASTA / "cenarios_validacao.json"
MD_RELATORIO = PASTA / "relatorio_mlmodel.md"
COPIA_MLMODEL = PASTA / "MLmodel_inspecionado.yaml"


def conferir_registry():
    """Confere a origem sem mudar os aliases."""

    client, tracking = configurar_registry()

    registro = json.loads(
        (
            RAIZ
            / "resultados"
            / "aula11_model_registry.json"
        ).read_text(encoding="utf-8")
    )

    version = client.get_model_version_by_alias(
        REGISTERED_MODEL_NAME,
        "production",
    )

    if str(version.version) != str(registro["version"]):
        raise RuntimeError(
            "O alias production nao aponta para "
            "a versao validada na Aula 11."
        )

    if version.run_id != registro["registration_run_id"]:
        raise RuntimeError(
            "Run de origem do modelo divergente."
        )

    return client, version, tracking


def baixar_modelo():
    """Recupera os arquivos da versao production."""

    caminho = mlflow.artifacts.download_artifacts(
        artifact_uri=MODEL_URI
    )

    pasta = Path(caminho)

    if not pasta.is_dir():
        raise RuntimeError(
            "Pacote de modelo nao encontrado."
        )

    return pasta


def inspecionar_pacote(pasta):
    """Le o MLmodel sem executar codigo do pacote."""

    arquivo = pasta / "MLmodel"

    if not arquivo.is_file():
        raise RuntimeError(
            "Arquivo MLmodel ausente."
        )

    conteudo = arquivo.read_text(
        encoding="utf-8"
    )

    configuracao = yaml.safe_load(
        conteudo
    )

    if not isinstance(configuracao, dict):
        raise RuntimeError(
            "MLmodel nao contem YAML valido."
        )

    flavors = configuracao.get("flavors", {})

    if not {
        "sklearn",
        "python_function",
    }.issubset(flavors):
        raise RuntimeError(
            "Flavors esperados nao encontrados."
        )

    inventario = []

    for item in sorted(pasta.rglob("*")):
        if item.is_file():
            inventario.append({
                "arquivo": item.relative_to(pasta).as_posix(),
                "tamanho_bytes": item.stat().st_size,
            })

    assinatura = configuracao.get(
        "signature"
    )

    if not assinatura:
        raise RuntimeError(
            "Signature nao encontrada no MLmodel."
        )

    sha256 = hashlib.sha256(
        arquivo.read_bytes()
    ).hexdigest()

    return {
        "configuracao": configuracao,
        "flavors": flavors,
        "inventario": inventario,
        "signature": assinatura,
        "mlmodel_sha256": sha256,
        "mlmodel_texto": conteudo,
    }


def inspecionar_contrato():
    """Recupera a assinatura pela API oficial."""

    info = get_model_info(MODEL_URI)

    if info.signature is None:
        raise RuntimeError(
            "Modelo registrado sem signature."
        )

    entradas = info.signature.inputs
    saidas = info.signature.outputs

    colunas = [
        {
            "name": coluna.name,
            "type": str(coluna.type),
            "required": bool(coluna.required),
        }
        for coluna in entradas.inputs
    ]

    return {
        "model_uri": MODEL_URI,
        "inputs": colunas,
        "outputs": (
            str(saidas) if saidas is not None
            else None
        ),
        "total_inputs": len(colunas),
    }


def validar_flavors():
    """Compara predicoes dos flavors sklearn/pyfunc."""

    cliente = novo_cliente()

    sklearn_model = mlflow.sklearn.load_model(
        MODEL_URI
    )

    pyfunc_model = mlflow.pyfunc.load_model(
        MODEL_URI
    )

    classe_sklearn = np.asarray(
        sklearn_model.predict(cliente)
    ).reshape(-1)

    classe_pyfunc = np.asarray(
        pyfunc_model.predict(cliente)
    ).reshape(-1)

    probabilidades = np.asarray(
        sklearn_model.predict_proba(cliente)
    )

    if (
        classe_sklearn.size != 1
        or classe_pyfunc.size != 1
        or probabilidades.shape != (1, 2)
    ):
        raise RuntimeError(
            "Formato de saida inesperado."
        )

    if int(classe_sklearn[0]) != int(classe_pyfunc[0]):
        raise RuntimeError(
            "Flavors produziram classes diferentes."
        )

    classe = int(classe_pyfunc[0])
    probabilidade = float(
        probabilidades[0, 1]
    )

    if not 0 <= probabilidade <= 1:
        raise RuntimeError(
            "Probabilidade invalida."
        )

    return {
        "classe_sklearn": classe,
        "classe_pyfunc": classe,
        "probabilidade_inadimplencia": probabilidade,
        "probabilidade_adimplencia": 1 - probabilidade,
    }


def validar_cenarios():
    """Testa caminho feliz, falta e excesso de colunas."""

    _, _, X_test, _, _ = carregar_dados()

    entrada_valida = X_test.head(3).copy()

    modelo = mlflow.pyfunc.load_model(
        MODEL_URI
    )

    resultado_valido = np.asarray(
        modelo.predict(entrada_valida)
    ).reshape(-1)

    if len(resultado_valido) != 3:
        raise RuntimeError(
            "Entrada valida nao gerou 3 previsoes."
        )

    entrada_incompleta = entrada_valida.drop(
        columns=["score_interno"]
    )

    erro_ausente = None

    try:
        modelo.predict(entrada_incompleta)
    except Exception as exc:
        erro_ausente = {
            "tipo": type(exc).__name__,
            "mensagem": str(exc)[:700],
        }

    if erro_ausente is None:
        raise RuntimeError(
            "Entrada sem coluna obrigatoria "
            "nao foi rejeitada."
        )

    entrada_extra = entrada_valida.copy()

    entrada_extra["canal_origem"] = "app"

    avisos = []

    with warnings.catch_warnings(
        record=True
    ) as capturados:

        warnings.simplefilter("always")

        resultado_extra = np.asarray(
            modelo.predict(entrada_extra)
        ).reshape(-1)

        avisos = [
            str(aviso.message)
            for aviso in capturados
        ]

    if len(resultado_extra) != 3:
        raise RuntimeError(
            "Entrada com coluna extra falhou."
        )

    # Se o MLflow ignorar a coluna extra,
    # as previsoes devem permanecer iguais.
    if not np.array_equal(
        resultado_valido,
        resultado_extra,
    ):
        raise RuntimeError(
            "Coluna extra alterou as previsoes."
        )

    return {
        "entrada_valida": {
            "quantidade_linhas": 3,
            "previsoes": [
                int(valor)
                for valor in resultado_valido
            ],
        },
        "coluna_ausente": {
            "coluna": "score_interno",
            "rejeitada": True,
            **erro_ausente,
        },
        "coluna_extra": {
            "coluna": "canal_origem",
            "aceita": True,
            "previsoes_preservadas": True,
            "avisos": avisos,
        },
    }


def executar():
    """Inspeciona e audita o modelo registrado."""

    client, versao, tracking = conferir_registry()

    pasta_modelo = baixar_modelo()

    pacote = inspecionar_pacote(
        pasta_modelo
    )

    contrato = inspecionar_contrato()

    flavors = validar_flavors()

    cenarios = validar_cenarios()

    if contrato["total_inputs"] != 8:
        raise RuntimeError(
            "A signature nao possui as 8 features "
            "esperadas neste projeto."
        )

    PASTA.mkdir(
        parents=True,
        exist_ok=True,
    )

    shutil.copy2(
        pasta_modelo / "MLmodel",
        COPIA_MLMODEL,
    )

    inventario = {
        "model_uri": MODEL_URI,
        "version": str(versao.version),
        "mlmodel_sha256": pacote["mlmodel_sha256"],
        "arquivos": pacote["inventario"],
    }

    JSON_INVENTARIO.write_text(
        json.dumps(
            inventario,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    JSON_CONTRATO.write_text(
        json.dumps(
            contrato,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    JSON_CENARIOS.write_text(
        json.dumps(
            cenarios,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    tabela = novo_cliente().copy()

    tabela["classe_prevista"] = (
        flavors["classe_pyfunc"]
    )

    tabela["probabilidade_inadimplencia"] = (
        flavors["probabilidade_inadimplencia"]
    )

    tabela.to_csv(
        CSV_PREVISOES,
        index=False,
        encoding="utf-8-sig",
    )

    nomes = [
        item["arquivo"]
        for item in pacote["inventario"]
    ]

    texto = f"""# Aula 13 - Formato MLmodel

## Modelo

Nome: {REGISTERED_MODEL_NAME}
Alias: production
Versao: {versao.version}
Run: {versao.run_id}

## Arquivos do pacote

{chr(10).join("- " + nome for nome in nomes)}

## Flavors

{chr(10).join("- " + f for f in pacote["flavors"])}

## Signature

Total de atributos: {contrato['total_inputs']}

{chr(10).join("- " + c["name"] + ": " + c["type"] for c in contrato["inputs"])}

## Inferencia

Classe prevista: {flavors['classe_pyfunc']}
Probabilidade de inadimplencia:
{flavors['probabilidade_inadimplencia']:.4%}

## Validacao de entrada

- Entrada valida: aceita
- Coluna score_interno ausente: rejeitada
- Coluna canal_origem extra: aceita
- Previsoes com coluna extra: preservadas

## Segurança

O modelo foi salvo em formato SKOPS.
O carregamento deve ser feito apenas de
fontes de modelo confiaveis.

## Proxima etapa

PyFunc personalizado e contrato de inferencia.

Este modelo usa dados sinteticos e nao pode
ser empregado em decisoes reais de credito.
"""

    MD_RELATORIO.write_text(
        texto,
        encoding="utf-8",
    )

    resultado = {
        "aula_local": 13,
        "model_uri": MODEL_URI,
        "registered_model_name": REGISTERED_MODEL_NAME,
        "version": str(versao.version),
        "registration_run_id": versao.run_id,
        "tracking_uri": tracking,
        "mlmodel_sha256": pacote["mlmodel_sha256"],
        "flavors": list(pacote["flavors"]),
        "serialization_format": (
            pacote["flavors"]["sklearn"].get(
                "serialization_format"
            )
        ),
        "total_arquivos": len(pacote["inventario"]),
        "signature_inputs": contrato["total_inputs"],
        "predicao": flavors,
        "cenarios": cenarios,
        "novas_runs": 0,
        "novas_versoes": 0,
        "novos_treinamentos": 0,
    }

    JSON_RESULTADO.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    JSON_RESULTADO.write_text(
        json.dumps(
            resultado,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n===== PACOTE MLMODEL =====")
    print("MODELO:", REGISTERED_MODEL_NAME)
    print("ALIAS: production")
    print("VERSAO:", versao.version)
    print("RUN:", versao.run_id)
    print("FLAVORS:", ", ".join(resultado["flavors"]))
    print("SERIALIZACAO:", resultado["serialization_format"])
    print("ARQUIVOS:", resultado["total_arquivos"])

    print("\n===== ARQUIVOS ENCONTRADOS =====")
    for nome in nomes:
        print("OK:", nome)

    print("\n===== CONTRATO DE ENTRADA =====")
    for coluna in contrato["inputs"]:
        print(
            coluna["name"],
            "|",
            coluna["type"],
            "| required:",
            coluna["required"],
        )

    print("\n===== INFERENCIA =====")
    print("CLASSE:", flavors["classe_pyfunc"])
    print(
        "PROBABILIDADE DE INADIMPLENCIA:",
        f"{flavors['probabilidade_inadimplencia']:.2%}",
    )
    print("SKLEARN E PYFUNC: CONSISTENTES")

    print("\n===== VALIDACAO =====")
    print("ENTRADA VALIDA: OK")
    print("COLUNA OBRIGATORIA AUSENTE: REJEITADA")
    print("COLUNA EXTRA: ACEITA")
    print("NOVAS RUNS: 0")
    print("NOVAS VERSOES: 0")
    print("NOVOS TREINAMENTOS: 0")

    return resultado


if __name__ == "__main__":
    executar()
