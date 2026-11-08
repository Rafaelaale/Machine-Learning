"""Auditoria documental do projeto didatico MLOps."""

import json
from datetime import datetime, timezone
from pathlib import Path

import mlflow
import yaml
from mlflow.tracking import MlflowClient

from src.aula04_primeira_run_mlflow import RAIZ


SAIDA = RAIZ / "resultados"
PIPELINE = SAIDA / "aula18_pipeline.json"
REMOTO = SAIDA / "aula19_servidor_remoto.json"


def carregar(caminho):
    if not caminho.is_file():
        raise FileNotFoundError(caminho)
    return json.loads(caminho.read_text(encoding="utf-8"))


def auditar():
    pipeline = carregar(PIPELINE)
    remoto = carregar(REMOTO)

    config = yaml.safe_load(
        (RAIZ / "MLproject").read_text(encoding="utf-8")
    )

    esperados = {"prepare", "train", "evaluate", "pipeline"}
    existentes = set(config["entry_points"])

    if not esperados.issubset(existentes):
        raise RuntimeError("MLproject incompleto.")

    if pipeline["status"] != "FINISHED":
        raise RuntimeError("Pipeline nao finalizado.")

    if remoto["status"] != "FINISHED":
        raise RuntimeError("Experimento HTTP nao finalizado.")

    if not remoto["artifact_verified"]:
        raise RuntimeError("Artefato remoto nao validado.")

    banco = RAIZ / "mlflow.db"

    if not banco.is_file():
        raise RuntimeError("Banco MLflow original ausente.")

    uri_local = "sqlite:///" + banco.resolve().as_posix()
    mlflow.set_tracking_uri(uri_local)

    client = MlflowClient(tracking_uri=uri_local)

    ids = {
        "parent": pipeline["parent_run_id"],
        "prepare": pipeline["prepare_run_id"],
        "train": pipeline["train_run_id"],
        "evaluate": pipeline["evaluate_run_id"],
    }

    runs = {}

    for etapa, run_id in ids.items():
        run = client.get_run(run_id)

        if run.info.status != "FINISHED":
            raise RuntimeError(
                f"Run {etapa} nao esta finalizado."
            )

        runs[etapa] = {
            "run_id": run_id,
            "status": run.info.status,
        }

    for etapa in ("prepare", "train", "evaluate"):
        run = client.get_run(ids[etapa])
        if run.data.tags.get("mlflow.parentRunId") != ids["parent"]:
            raise RuntimeError(
                f"Run {etapa} nao esta vinculado ao pai."
            )

    versao = client.get_model_version(
        name=pipeline["registered_model_name"],
        version=pipeline["registered_version"],
    )

    if versao.run_id != ids["train"]:
        raise RuntimeError(
            "Versao registrada nao corresponde ao treinamento."
        )

    evidencias = {
        "mlproject": (RAIZ / "MLproject").is_file(),
        "python_env": (RAIZ / "python_env.yaml").is_file(),
        "prepare": (RAIZ / "src/aula17_prepare_data.py").is_file(),
        "train": (RAIZ / "src/aula17_train.py").is_file(),
        "evaluate": (RAIZ / "src/aula18_evaluate.py").is_file(),
        "pipeline": (RAIZ / "src/aula18_run_pipeline.py").is_file(),
        "cliente_http": (
            RAIZ / "src/aula19_cliente_remoto.py"
        ).is_file(),
        "relatorio_pipeline": PIPELINE.is_file(),
        "relatorio_tracking_http": REMOTO.is_file(),
        "backend_sqlite": banco.is_file(),
        "artifact_http_verificado": remoto["artifact_verified"],
    }

    if not all(evidencias.values()):
        raise RuntimeError("Evidencias obrigatorias incompletas.")

    maturidade = {
        "tracking_experimentos": "validado",
        "model_registry": "validado",
        "mlflow_projects": "validado",
        "pipeline_reproduzivel": "validado",
        "api_rest": "validada_em_aula_anterior",
        "docker_serving": "validado_em_aula_anterior",
        "tracking_http_local": "validado",
        "servidor_remoto_real": "nao_implementado",
        "postgresql": "nao_implementado",
        "object_storage_cloud": "nao_implementado",
        "autenticacao_corporativa": "nao_implementada",
        "cicd_externo": "nao_implementado",
        "monitoramento_producao": "nao_implementado",
        "fairness_com_dados_reais": "nao_implementada",
        "aprovacao_formal_modelo": "nao_implementada",
    }

    resultado = {
        "aula": 20,
        "status": "AUDITORIA_CONCLUIDA",
        "gerado_em_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "escopo": "laboratorio_didatico_local",
        "pipeline_id": pipeline["pipeline_id"],
        "model_uri": pipeline["model_uri"],
        "registered_model_name": pipeline["registered_model_name"],
        "registered_version": str(
            pipeline["registered_version"]
        ),
        "runs": runs,
        "tracking_http": remoto["tracking_uri"],
        "tracking_http_run_id": remoto["run_id"],
        "metrics": pipeline["metrics"],
        "entry_points": sorted(esperados),
        "evidencias": evidencias,
        "maturidade": maturidade,
        "producao_aprovada": False,
    }

    SAIDA.mkdir(parents=True, exist_ok=True)

    destino = SAIDA / "aula20_auditoria_mlops.json"
    destino.write_text(
        json.dumps(
            resultado,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8",
    )

    card = f"""# Model Card - Risco de credito

## Identificacao
- Projeto: MLflow - Gestao e Rastreabilidade
- Modelo: {pipeline['registered_model_name']}
- Versao: {pipeline['registered_version']}
- Model URI: `{pipeline['model_uri']}`
- Pipeline ID: `{pipeline['pipeline_id']}`

## Objetivo
Classificacao didatica de inadimplencia com dados sinteticos.

## Dados
- Amostras: {pipeline['parameters']['n_samples']}
- Proporcao de teste: {pipeline['parameters']['test_size']}
- Semente: {pipeline['parameters']['random_state']}

## Metricas da avaliacao
- ROC-AUC: {pipeline['metrics']['roc_auc_teste']:.4f}
- Acuracia: {pipeline['metrics']['accuracy_teste']:.4f}
- Precisao: {pipeline['metrics']['precision_inadimplente']:.4f}
- Recall: {pipeline['metrics']['recall_inadimplente']:.4f}
- F1: {pipeline['metrics']['f1_inadimplente']:.4f}

## Rastreabilidade
- Parent run: `{ids['parent']}`
- Prepare run: `{ids['prepare']}`
- Train run: `{ids['train']}`
- Evaluate run: `{ids['evaluate']}`

## Limitacoes
- Dados sinteticos nao representam toda a populacao real.
- Nao houve validacao com dados reais de credito.
- Nao houve analise completa de fairness, bias ou drift.
- Nao existe aprovacao regulatoria ou corporativa.
- Nao foram estabelecidos SLAs de producao.

## Uso permitido
Demonstracao, estudo, testes e portfolio tecnico.

## Uso nao aprovado
Decisoes reais de concessao de credito.

## Governanca
Nenhuma promocao automatica para producao.
Aprovacao humana e avaliacao de riscos sao necessarias.
"""

    (RAIZ / "anotacoes/aula20_model_card.md").write_text(
        card,
        encoding="utf-8",
    )

    matriz = [
        "# Aula 20 - Matriz de maturidade MLOps",
        "",
        "Auditoria do laboratorio local.",
        "",
        "| Componente | Situacao |",
        "|---|---|",
    ]

    for componente, situacao in maturidade.items():
        matriz.append(
            f"| {componente} | {situacao} |"
        )

    matriz += [
        "",
        "## Proximos passos opcionais",
        "1. Validacao automatizada de qualidade de dados.",
        "2. Monitoramento de drift e latencia.",
        "3. Aprovacao formal de modelos.",
        "4. Integracao com CI/CD.",
        "5. Tracking Server corporativo autenticado.",
        "6. Politica de rollback.",
        "",
        "Nenhuma dessas etapas foi declarada como concluida.",
    ]

    (RAIZ / "anotacoes/aula20_maturidade_mlops.md").write_text(
        "\n".join(matriz) + "\n",
        encoding="utf-8",
    )

    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Aula 20 - MLflow na stack MLOps\n",
                    "Auditoria final e governanca do laboratorio.\n",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "import json\n",
                    "from pathlib import Path\n",
                    "raiz = Path.cwd()\n",
                    "if raiz.name == 'notebooks': raiz = raiz.parent\n",
                    "arquivo = raiz / 'resultados/aula20_auditoria_mlops.json'\n",
                    "auditoria = json.loads(arquivo.read_text(encoding='utf-8'))\n",
                    "auditoria['maturidade']\n",
                ],
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": [
                    "print('MODELO:', auditoria['model_uri'])\n",
                    "print('RUNS:', auditoria['runs'])\n",
                    "print('METRICAS:', auditoria['metrics'])\n",
                    "print('PRODUCAO APROVADA:', auditoria['producao_aprovada'])\n",
                ],
            },
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            }
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    arquivo_nb = RAIZ / "notebooks/20_stack_mlops.ipynb"
    arquivo_nb.write_text(
        json.dumps(notebook, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("AUDITORIA:", destino)
    print("MODELO:", resultado["model_uri"])
    print("RUNS VERIFICADOS:", len(runs))
    print("EVIDENCIAS:", len(evidencias))
    print("PRODUCAO APROVADA: NAO")
    print("MODEL CARD: GERADO")
    print("MATRIZ MLOPS: GERADA")
    print("NOTEBOOK: GERADO")
    print("AUDITORIA CONCLUIDA")

    return resultado


if __name__ == "__main__":
    auditar()
