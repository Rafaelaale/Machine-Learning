from kfp import compiler, dsl


@dsl.component(base_image="python:3.11-slim")
def preparar_dados() -> list:
    return [2.0, 4.0, 6.0, 8.0, 10.0]


@dsl.component(base_image="python:3.11-slim")
def calcular_media(valores: list) -> float:
    media = sum(valores) / len(valores)
    print(f"Media calculada: {media}")
    return media


@dsl.pipeline(name="primeiro-pipeline-machine-learning")
def pipeline_ml():
    dados = preparar_dados()
    calcular_media(valores=dados.output)


if __name__ == "__main__":
    compiler.Compiler().compile(
        pipeline_func=pipeline_ml,
        package_path="pipelines/primeiro_pipeline.yaml",
    )
    print("PIPELINE COMPILADO COM SUCESSO")
