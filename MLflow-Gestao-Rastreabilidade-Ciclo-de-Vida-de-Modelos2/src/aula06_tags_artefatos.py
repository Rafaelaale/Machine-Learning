"""Aula 06 - Tags e artefatos no MLflow.

Nova run de regressao logistica, preservando v1.
Registra parametros, metricas, tags e oito artefatos.
"""

import json
from pathlib import Path
from urllib.parse import urlparse

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import mlflow
import pandas as pd

from mlflow.tracking import MlflowClient

from sklearn.metrics import (
    ConfusionMatrixDisplay,
    RocCurveDisplay,
    classification_report,
)
from sklearn.model_selection import (
    StratifiedKFold,
    cross_val_score,
)

from src.aula04_primeira_run_mlflow import (
    RAIZ,
    RANDOM_STATE,
    TARGET,
    FEATURES,
    carregar_dados,
    construir_pipeline,
    configurar_tracking,
)

from src.aula05_logging_manual import (
    EXPERIMENTO,
    preparar_parametros,
    preparar_metricas,
)


RUN_NAME = "aula03_lr_manual_v2"

TAGS = {
    "project": "risco_credito",
    "course_lesson": "aula_03",
    "dataset_version": "synthetic_credit_v1",
    "model_family": "linear_model",
    "task": "binary_classification",
    "target": "inadimplente",
    "tracking_type": "manual",
    "run_purpose": "baseline_with_manual_artifacts",
}

ARTEFATOS = [
    "reports/classification_report.txt",
    "reports/classification_report.json",
    "reports/run_summary.md",
    "plots/matriz_confusao.png",
    "plots/curva_roc.png",
    "plots/coeficientes_modelo.png",
    "tables/coeficientes_modelo.json",
    "data/dataset_profile.json",
]

PASTA_LOCAL = RAIZ / "resultados" / "aula06_artefatos"
RELATORIO = RAIZ / "resultados" / "aula06_tags_artefatos.json"


def verificar_armazenamento():
    """Confere o experimento e seu destino de artefatos."""

    uri = configurar_tracking()

    client = MlflowClient()

    exp = client.get_experiment_by_name(
        EXPERIMENTO
    )

    if exp is None:
        raise RuntimeError(
            "Experimento anterior nao encontrado."
        )

    local = exp.artifact_location
    esquema = urlparse(local).scheme.lower()

    print("TRACKING:", uri)
    print("ARTIFACT LOCATION:", local)

    if esquema not in ("file", ""):
        raise RuntimeError(
            "O experimento existente nao utiliza "
            "um artifact store local acessivel "
            "diretamente: "
            + str(local)
            + ". Nao altere o banco SQLite nem "
            "crie outro experimento automaticamente."
        )

    return client, exp


def artefatos_remotos(client, run_id):
    """Lista os caminhos completos dos artefatos."""

    encontrados = set()

    def visitar(pasta=""):
        for item in client.list_artifacts(
            run_id,
            path=pasta,
        ):
            if item.is_dir:
                visitar(item.path)
            else:
                encontrados.add(
                    item.path.replace("\\", "/")
                )

    visitar()
    return encontrados


def consultar_run_anterior(client, exp):
    """Reutiliza a v2 apenas se estiver completa."""

    if not RELATORIO.is_file():
        return None

    relatorio = json.loads(
        RELATORIO.read_text(encoding="utf-8")
    )

    run = client.get_run(relatorio["run_id"])

    assert run.info.experiment_id == exp.experiment_id
    assert run.info.status == "FINISHED"
    assert run.data.tags["mlflow.runName"] == RUN_NAME

    for chave, valor in TAGS.items():
        assert run.data.tags.get(chave) == valor

    assert len(run.data.params) == 18
    assert len(run.data.metrics) == 11

    encontrados = artefatos_remotos(
        client,
        run.info.run_id,
    )

    ausentes = set(ARTEFATOS) - encontrados

    if ausentes:
        raise RuntimeError(
            "A run anterior nao possui todos os "
            f"artefatos: {sorted(ausentes)}"
        )

    print("\nRUN V2 EXISTENTE VALIDADA")
    print("RUN ID:", run.info.run_id)
    print("ARTEFATOS:", len(ARTEFATOS))
    print("NENHUMA RUN DUPLICADA")

    return relatorio


def salvar_local(caminho, conteudo):
    """Guarda copia legivel no projeto."""

    caminho.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not caminho.exists():
        caminho.write_text(
            conteudo,
            encoding="utf-8",
        )


def construir_perfil(df):
    """Documenta o dataset sintetico usado."""

    distribuicao = (
        df[TARGET]
        .value_counts(normalize=True)
        .round(4)
        .to_dict()
    )

    return {
        "dataset_version": "synthetic_credit_v1",
        "n_amostras": int(len(df)),
        "n_colunas": int(df.shape[1]),
        "target": TARGET,
        "features": list(FEATURES),
        "num_cols": [
            "idade",
            "renda_mensal",
            "tempo_emprego_anos",
            "score_interno",
            "valor_solicitado",
            "num_parcelas",
        ],
        "cat_cols": [
            "tipo_renda",
            "possui_restricao",
        ],
        "target_distribution": {
            str(chave): float(valor)
            for chave, valor in distribuicao.items()
        },
        "dtypes": (
            df.dtypes.astype(str).to_dict()
        ),
    }


def gerar_resumo(df, X_train, X_test, metrics):
    """Prepara o resumo legivel da execucao."""

    return f"""# Resumo da run

## Contexto

Projeto: risco de credito
Objetivo: baseline com tracking manual enriquecido
Run: {RUN_NAME}
Modelo: Regressao Logistica
Target: {TARGET}

## Dados

- Amostras totais: {len(df)}
- Treino: {len(X_train)}
- Teste: {len(X_test)}
- Dataset version: synthetic_credit_v1

## Principais metricas

- ROC-AUC teste: {metrics['roc_auc_teste']:.4f}
- ROC-AUC CV media: {metrics['roc_auc_cv_media']:.4f}
- ROC-AUC CV desvio: {metrics['roc_auc_cv_desvio']:.4f}
- Precision inadimplente: {metrics['precision_inadimplente']:.4f}
- Recall inadimplente: {metrics['recall_inadimplente']:.4f}
- F1 inadimplente: {metrics['f1_inadimplente']:.4f}

## Matriz de confusao

- TN: {int(metrics['tn'])}
- FP: {int(metrics['fp'])}
- FN: {int(metrics['fn'])}
- TP: {int(metrics['tp'])}

## Leitura inicial

Este modelo funciona como baseline rastreavel.
A ROC-AUC avalia a ordenacao dos casos por risco.
Precision e recall devem ser interpretados com
os custos dos falsos positivos e falsos negativos.

Os dados sao sinteticos, para fins educacionais.
O modelo nao foi validado para decisao real de credito.
"""


def registrar_artefatos(
    df,
    X_train,
    X_test,
    y_test,
    y_pred,
    y_proba,
    model_pipe,
    metrics,
):
    """Cria e registra os oito artefatos da aula."""

    # 1 e 2: relatorios de classificacao.
    texto = classification_report(
        y_test,
        y_pred,
        labels=[0, 1],
        target_names=["adimplente", "inadimplente"],
        zero_division=0,
    )

    dicionario = classification_report(
        y_test,
        y_pred,
        labels=[0, 1],
        target_names=["adimplente", "inadimplente"],
        output_dict=True,
        zero_division=0,
    )

    mlflow.log_text(
        texto,
        "reports/classification_report.txt",
    )

    mlflow.log_dict(
        dicionario,
        "reports/classification_report.json",
    )

    salvar_local(
        PASTA_LOCAL / "reports/classification_report.txt",
        texto,
    )

    salvar_local(
        PASTA_LOCAL / "reports/classification_report.json",
        json.dumps(
            dicionario,
            ensure_ascii=False,
            indent=2,
        ),
    )

    # 3: matriz de confusao.
    fig, ax = plt.subplots(figsize=(6, 5))

    ConfusionMatrixDisplay.from_predictions(
        y_test,
        y_pred,
        labels=[0, 1],
        display_labels=["adimplente", "inadimplente"],
        ax=ax,
    )

    ax.set_title("Matriz de confusao - teste")
    fig.tight_layout()

    mlflow.log_figure(
        fig,
        "plots/matriz_confusao.png",
    )

    caminho = (
        PASTA_LOCAL / "plots/matriz_confusao.png"
    )

    caminho.parent.mkdir(parents=True, exist_ok=True)
    if not caminho.exists():
        fig.savefig(caminho, dpi=150)

    plt.close(fig)

    # 4: curva ROC.
    fig, ax = plt.subplots(figsize=(6, 5))

    RocCurveDisplay.from_predictions(
        y_test,
        y_proba,
        name="LogisticRegression",
        ax=ax,
    )

    ax.set_title("Curva ROC - teste")
    fig.tight_layout()

    mlflow.log_figure(
        fig,
        "plots/curva_roc.png",
    )

    caminho = (
        PASTA_LOCAL / "plots/curva_roc.png"
    )

    if not caminho.exists():
        fig.savefig(caminho, dpi=150)

    plt.close(fig)

    # 5 e 6: tabela e grafico de coeficientes.
    prep = model_pipe.named_steps["prep"]
    model = model_pipe.named_steps["model"]

    feature_names = prep.get_feature_names_out()

    coef_df = (
        pd.DataFrame({
            "feature": feature_names,
            "coeficiente": model.coef_.ravel(),
        })
        .sort_values("coeficiente")
        .reset_index(drop=True)
    )

    mlflow.log_table(
        coef_df,
        "tables/coeficientes_modelo.json",
    )

    salvar_local(
        PASTA_LOCAL / "tables/coeficientes_modelo.json",
        coef_df.to_json(
            orient="records",
            force_ascii=False,
            indent=2,
        ),
    )

    fig, ax = plt.subplots(figsize=(9, 6))

    coef_df.plot(
        kind="barh",
        x="feature",
        y="coeficiente",
        legend=False,
        ax=ax,
    )

    ax.axvline(0, linewidth=0.8)
    ax.set_title("Coeficientes do modelo")
    ax.set_xlabel("Coeficiente")
    ax.set_ylabel("")
    fig.tight_layout()

    mlflow.log_figure(
        fig,
        "plots/coeficientes_modelo.png",
    )

    caminho = (
        PASTA_LOCAL / "plots/coeficientes_modelo.png"
    )

    if not caminho.exists():
        fig.savefig(caminho, dpi=150)

    plt.close(fig)

    # 7: perfil do dataset.
    perfil = construir_perfil(df)

    mlflow.log_dict(
        perfil,
        "data/dataset_profile.json",
    )

    salvar_local(
        PASTA_LOCAL / "data/dataset_profile.json",
        json.dumps(
            perfil,
            ensure_ascii=False,
            indent=2,
        ),
    )

    # 8: resumo em Markdown.
    resumo = gerar_resumo(
        df,
        X_train,
        X_test,
        metrics,
    )

    mlflow.log_text(
        resumo,
        "reports/run_summary.md",
    )

    salvar_local(
        PASTA_LOCAL / "reports/run_summary.md",
        resumo,
    )

    return coef_df


def executar():
    """Treina baseline v2 e audita os registros."""

    client, experimento = verificar_armazenamento()

    anterior = consultar_run_anterior(
        client,
        experimento,
    )

    if anterior is not None:
        return anterior

    if mlflow.active_run() is not None:
        raise RuntimeError(
            "Ha uma run ativa neste processo. "
            "Encerre-a antes de iniciar a Aula 06."
        )

    (
        df,
        X_train,
        X_test,
        y_train,
        y_test,
    ) = carregar_dados()

    model_pipe = construir_pipeline()

    params = preparar_parametros(
        df,
        X_train,
        X_test,
    )

    print("\n===== INICIANDO RUN V2 =====")
    print("EXPERIMENTO:", EXPERIMENTO)
    print("RUN:", RUN_NAME)

    with mlflow.start_run(
        run_name=RUN_NAME
    ) as run:

        model_pipe.fit(X_train, y_train)

        y_pred = model_pipe.predict(X_test)

        y_proba = (
            model_pipe.predict_proba(X_test)[:, 1]
        )

        cv = StratifiedKFold(
            n_splits=5,
            shuffle=True,
            random_state=RANDOM_STATE,
        )

        scores = cross_val_score(
            construir_pipeline(),
            X_train,
            y_train,
            cv=cv,
            scoring="roc_auc",
            n_jobs=1,
        )

        metrics = preparar_metricas(
            y_test,
            y_pred,
            y_proba,
            scores,
        )

        mlflow.log_params(params)
        mlflow.log_metrics(metrics)
        mlflow.set_tags(TAGS)

        coeficientes = registrar_artefatos(
            df,
            X_train,
            X_test,
            y_test,
            y_pred,
            y_proba,
            model_pipe,
            metrics,
        )

        run_id = run.info.run_id

    # Inspeciona os dados ja persistidos pelo MLflow.
    run_registrada = client.get_run(run_id)

    assert run_registrada.info.status == "FINISHED"

    encontrados = artefatos_remotos(
        client,
        run_id,
    )

    ausentes = set(ARTEFATOS) - encontrados

    if ausentes:
        raise RuntimeError(
            "Artefatos nao encontrados: "
            + str(sorted(ausentes))
        )

    for chave, valor in TAGS.items():
        assert run_registrada.data.tags[chave] == valor

    assert len(run_registrada.data.params) == 18
    assert len(run_registrada.data.metrics) == 11

    relatorio = {
        "aula_local": 6,
        "aula_codigo_alura": 3,
        "experimento": EXPERIMENTO,
        "run_name": RUN_NAME,
        "run_id": run_id,
        "experiment_id": experimento.experiment_id,
        "artifact_uri": run_registrada.info.artifact_uri,
        "params": params,
        "metrics": metrics,
        "tags": TAGS,
        "artefatos": ARTEFATOS,
        "quantidade_coeficientes": len(coeficientes),
        "status": "FINISHED",
    }

    RELATORIO.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    RELATORIO.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n===== RUN V2 VALIDADA =====")
    print("RUN ID:", run_id)
    print("STATUS:", run_registrada.info.status)
    print("PARAMETROS:", len(params))
    print("METRICAS:", len(metrics))
    print("TAGS PERSONALIZADAS:", len(TAGS))
    print("ARTEFATOS:", len(ARTEFATOS))
    print("COEFICIENTES:", len(coeficientes))

    print("\nROC-AUC TESTE:")
    print(f"{metrics['roc_auc_teste']:.4f}")

    print("\nPRECISION INADIMPLENTE:")
    print(f"{metrics['precision_inadimplente']:.4f}")

    print("\nRECALL INADIMPLENTE:")
    print(f"{metrics['recall_inadimplente']:.4f}")

    print("\nMATRIZ DE CONFUSAO:")
    for chave in ("tn", "fp", "fn", "tp"):
        print(chave.upper(), int(metrics[chave]))

    print("\nARTEFATOS REGISTRADOS:")
    for arquivo in ARTEFATOS:
        print("OK:", arquivo)

    return relatorio


if __name__ == "__main__":
    executar()
