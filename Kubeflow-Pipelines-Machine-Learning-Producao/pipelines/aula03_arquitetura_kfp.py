"""Aula 03 - Exemplo introdutorio de Kubeflow Pipelines V2.

Este arquivo define componentes e dependencias.
A compilacao requer a instalacao do SDK kfp.
"""

from kfp import compiler, dsl


@dsl.component(base_image="python:3.12-slim")
def preprocess(dataset: str) -> str:
    """Simula a preparacao dos dados."""
    print("Preparando dados:", dataset)
    return f"{dataset}_processado"


@dsl.component(base_image="python:3.12-slim")
def train(dataset: str) -> str:
    """Simula o treinamento de um modelo."""
    print("Treinando com:", dataset)
    return "modelo_treinado"


@dsl.pipeline(name="aula03-arquitetura-kubeflow")
def pipeline_ml(dataset: str = "dados_sinteticos") -> str:
    preparacao = preprocess(dataset=dataset)
    treinamento = train(dataset=preparacao.output)
    return treinamento.output


def compilar(destino="pipelines/aula03_pipeline_compilado.yaml"):
    """Compila a definicao para o formato KFP V2."""
    compiler.Compiler().compile(
        pipeline_func=pipeline_ml,
        package_path=destino,
    )
    return destino


if __name__ == "__main__":
    resultado = compilar()
    print("PIPELINE COMPILADO:", resultado)
