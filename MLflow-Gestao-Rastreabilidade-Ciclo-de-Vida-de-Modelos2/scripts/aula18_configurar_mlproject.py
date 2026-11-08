"""Adiciona evaluate/pipeline e protege relatorios das aulas anteriores."""

import shutil
from pathlib import Path

from src.aula04_primeira_run_mlflow import RAIZ


def backup(path):
    copia = path.with_suffix(path.suffix + ".bak_aula18")
    if not copia.exists():
        shutil.copy2(path, copia)
        print("BACKUP:", copia.name)


def alterar(path, anterior, novo):
    conteudo = path.read_text(encoding="utf-8-sig")

    if novo in conteudo:
        print("AJUSTE EXISTENTE:", path.name)
        return

    if anterior not in conteudo:
        raise RuntimeError(
            "Trecho esperado nao encontrado em " + str(path)
        )

    backup(path)
    path.write_text(
        conteudo.replace(anterior, novo, 1),
        encoding="utf-8",
    )
    print("AJUSTADO:", path.name)


mlproject = RAIZ / "MLproject"
conteudo = mlproject.read_text(encoding="utf-8-sig")

# No Windows, evita que o MLflow Projects acione
# acidentalmente o Python 3.14 global.
original_python = "python -m src.aula17_"
correct_python = ".venv/Scripts/python.exe -m src.aula17_"

if original_python in conteudo:
    backup(mlproject)
    conteudo = conteudo.replace(original_python, correct_python)

if "  evaluate:" not in conteudo:
    backup(mlproject)

    conteudo += """
  evaluate:
    parameters:
      model_uri: {type: str}
      data_dir: {type: path, default: "data/processed/manual"}
      threshold: {type: float, default: 0.5}
      pipeline_id: {type: str, default: "manual"}
    command: >
      .venv/Scripts/python.exe -m src.aula18_evaluate
      --model-uri {model_uri}
      --data-dir {data_dir}
      --threshold {threshold}
      --pipeline-id {pipeline_id}

  pipeline:
    parameters:
      model_name: {type: str, default: "random_forest"}
      n_samples: {type: int, default: 6000}
      test_size: {type: float, default: 0.25}
      random_state: {type: int, default: 42}
      threshold: {type: float, default: 0.5}
      registered_model_name: {type: str, default: "risco_credito_project_model"}
    command: >
      .venv/Scripts/python.exe -m src.aula18_run_pipeline
      --model-name {model_name}
      --n-samples {n_samples}
      --test-size {test_size}
      --random-state {random_state}
      --threshold {threshold}
      --registered-model-name {registered_model_name}
"""

    conteudo = conteudo.rstrip() + "\n"

mlproject.write_text(conteudo, encoding="utf-8")
print("MLPROJECT: 4 ENTRY POINTS")

# Os scripts da Aula 17 escreviam sempre no mesmo JSON.
# Para pipelines da Aula 18, salvamos separadamente.
prepare = RAIZ / "src" / "aula17_prepare_data.py"

alterar(
    prepare,
    '''    (RAIZ / "resultados" / "aula17_prepare.json").write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )''',
    '''    if pipeline_id.startswith("aula18_"):
        relatorio = (
            RAIZ / "resultados" / "aula18_pipeline"
            / pipeline_id / "prepare.json"
        )
        relatorio.parent.mkdir(parents=True, exist_ok=True)
    else:
        relatorio = RAIZ / "resultados" / "aula17_prepare.json"

    relatorio.write_text(
        json.dumps(resultado, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )''',
)

train = RAIZ / "src" / "aula17_train.py"

alterar(
    train,
    '''    relatorio = (
        RAIZ / "resultados" / "aula17_train.json"
    )

    relatorio.write_text(''',
    '''    if pipeline_id.startswith("aula18_"):
        relatorio = (
            RAIZ / "resultados" / "aula18_pipeline"
            / pipeline_id / "train.json"
        )
        relatorio.parent.mkdir(parents=True, exist_ok=True)
    else:
        relatorio = RAIZ / "resultados" / "aula17_train.json"

    relatorio.write_text(''',
)

print("RELATORIOS ANTERIORES: PRESERVADOS")
