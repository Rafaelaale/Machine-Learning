"""Corrige caminhos COPY gerados pelo MLflow no Windows.

A correcao ocorre somente no Dockerfile temporario
antes de chamar o Docker build.
"""

import re
from pathlib import Path

import mlflow.models
from mlflow.models import docker_utils

from src.aula04_primeira_run_mlflow import RAIZ


MODEL_PATH = (
    RAIZ
    / "resultados"
    / "aula16_docker"
    / "modelo_empacotado"
)

IMAGE = "risco-credito-serving:latest"

if not (MODEL_PATH / "MLmodel").is_file():
    raise RuntimeError(
        "Pacote MLmodel nao encontrado."
    )

original_build = docker_utils.build_image_from_context


def build_corrigido(*args, **kwargs):
    """Inspeciona e corrige o COPY antes do build."""

    context_dir = kwargs.get("context_dir")

    if context_dir is None and args:
        context_dir = args[0]

    if context_dir is None:
        raise RuntimeError(
            "Contexto Docker nao identificado."
        )

    pasta = Path(context_dir)
    dockerfile = pasta / "Dockerfile"

    if not dockerfile.is_file():
        raise RuntimeError(
            f"Dockerfile ausente: {dockerfile}"
        )

    conteudo = dockerfile.read_text(
        encoding="utf-8"
    )

    alteracoes = []

    def corrigir(match):
        origem = match.group(2)

        if "\\" not in origem:
            return match.group(0)

        corrigida = origem.replace("\\", "/")

        if not (pasta / corrigida).exists():
            raise RuntimeError(
                "A origem do COPY nao existe: "
                f"{pasta / corrigida}"
            )

        alteracoes.append(
            (origem, corrigida)
        )

        return (
            match.group(1)
            + corrigida
            + match.group(3)
        )

    padrao = (
        r"(?m)^(\s*COPY\s+)"
        r"(\S+)"
        r"(\s+/opt/ml/model\s*)$"
    )

    corrigido = re.sub(
        padrao,
        corrigir,
        conteudo,
    )

    if alteracoes:
        dockerfile.write_text(
            corrigido,
            encoding="utf-8",
        )

        for antes, depois in alteracoes:
            print(
                "COPY ORIGINAL:",
                antes,
                flush=True,
            )
            print(
                "COPY CORRIGIDO:",
                depois,
                flush=True,
            )
    else:
        print(
            "Dockerfile nao precisou de ajuste.",
            flush=True,
        )

    return original_build(
        *args,
        **kwargs,
    )


docker_utils.build_image_from_context = build_corrigido

print("MODELO:", MODEL_PATH, flush=True)
print("IMAGEM:", IMAGE, flush=True)
print("INICIANDO BUILD COM CORRECAO WINDOWS", flush=True)

mlflow.models.build_docker(
    model_uri=str(MODEL_PATH),
    name=IMAGE,
    env_manager="virtualenv",
)

print(
    "IMAGEM DOCKER CONSTRUIDA COM SUCESSO",
    flush=True,
)