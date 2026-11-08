"""Aula 04 - Primeira run no MLflow.

Treina a regressao logistica preparada na Aula 03.
Registra parametros e metricas no MLflow Tracking.

Usa armazenamento local exclusivo deste projeto.
Nao registra modelos ou artefatos nesta etapa.
"""

import json
from pathlib import Path

import mlflow
import numpy as np
import pandas as pd

from sklearn.metrics import (
    classification_report,
    roc_auc_score,
)
from sklearn.model_selection import (
    StratifiedKFold,
    cross_val_score,
)

from src.aula03_ambiente_dataset import (
    RAIZ,
    RANDOM_STATE,
    TARGET,
    FEATURES,
    construir_pipeline,
)


DADOS = RAIZ / "dados"
RESULTADOS = RAIZ / "resultados"
MLRUNS = RAIZ / "mlruns"

EXPERIMENTO = "risco_credito_baseline"
NOME_RUN = "baseline_regressao_logistica"

ARQUIVO_RELATORIO = (
    RESULTADOS / "aula04_primeira_run_mlflow.json"
)

ARQUIVO_PREVISOES = (
    RESULTADOS / "aula04_previsoes_baseline.csv"
)

ARQUIVO_CLASSIFICACAO = (
    RESULTADOS / "aula04_classification_report.json"
)


def configurar_tracking():
    """Usa URI absoluta para o tracking local."""

    MLRUNS.mkdir(parents=True, exist_ok=True)

    tracking_uri = f"sqlite:///{(RAIZ / 'mlflow.db').resolve().as_posix()}"

    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(EXPERIMENTO)

    return tracking_uri


def carregar_dados():
    """Recupera os dados preparados na Aula 03."""

    treino = pd.read_csv(
        DADOS / "aula03_treino_credito.csv"
    )

    teste = pd.read_csv(
        DADOS / "aula03_teste_credito.csv"
    )

    base = pd.read_csv(
        DADOS / "aula03_base_credito_sintetica.csv"
    )

    if len(base) != 6000:
        raise ValueError("Base deve ter 6000 registros.")

    if len(treino) != 4500:
        raise ValueError("Treino deve ter 4500 registros.")

    if len(teste) != 1500:
        raise ValueError("Teste deve ter 1500 registros.")

    for nome, tabela in (
        ("base", base),
        ("treino", treino),
        ("teste", teste),
    ):
        if set(tabela.columns) != set(FEATURES + [TARGET]):
            raise ValueError(
                f"Colunas invalidas em {nome}."
            )

        if tabela.isna().any().any():
            raise ValueError(
                f"Valores ausentes em {nome}."
            )

        if set(tabela[TARGET].unique()) != {0, 1}:
            raise ValueError(
                f"Classes incorretas em {nome}."
            )

    X_train = treino[FEATURES]
    y_train = treino[TARGET]

    X_test = teste[FEATURES]
    y_test = teste[TARGET]

    return (
        base,
        X_train,
        X_test,
        y_train,
        y_test,
    )


def novo_cliente():
    """Perfil sintetico apresentado na transcricao."""

    return pd.DataFrame([
        {
            "idade": 34,
            "renda_mensal": 4200.0,
            "tempo_emprego_anos": 5.0,
            "score_interno": 620,
            "valor_solicitado": 12000.0,
            "num_parcelas": 24,
            "tipo_renda": "CLT",
            "possui_restricao": "nao",
        }
    ])[FEATURES]


def calcular_metricas(
    model_pipe,
    X_train,
    X_test,
    y_train,
    y_test,
):
    """Calcula metricas de teste e validacao cruzada."""

    # O pipeline ainda nao foi treinado.
    model_pipe.fit(X_train, y_train)

    y_proba = model_pipe.predict_proba(X_test)[:, 1]
    y_pred = model_pipe.predict(X_test)

    roc_auc_teste = roc_auc_score(
        y_test,
        y_proba,
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

    report = classification_report(
        y_test,
        y_pred,
        target_names=[
            "adimplente",
            "inadimplente",
        ],
        output_dict=True,
        zero_division=0,
    )

    metricas = {
        "roc_auc_teste": float(roc_auc_teste),
        "roc_auc_cv_media": float(scores.mean()),
        "roc_auc_cv_desvio": float(scores.std()),
        "accuracy_teste": float(report["accuracy"]),
        "precision_inadimplente": float(
            report["inadimplente"]["precision"]
        ),
        "recall_inadimplente": float(
            report["inadimplente"]["recall"]
        ),
        "f1_inadimplente": float(
            report["inadimplente"]["f1-score"]
        ),
    }

    return (
        metricas,
        report,
        y_pred,
        y_proba,
    )


def verificar_run_anterior():
    """Evita duplicar uma run concluida da mesma aula."""

    if not ARQUIVO_RELATORIO.is_file():
        return None

    relatorio = json.loads(
        ARQUIVO_RELATORIO.read_text(encoding="utf-8")
    )

    run_id = relatorio.get("run_id")

    if not run_id:
        raise ValueError(
            "Relatorio existente sem run_id."
        )

    client = mlflow.tracking.MlflowClient()

    registrada = client.get_run(run_id)

    if registrada.info.status != "FINISHED":
        raise ValueError(
            "Run anterior nao esta concluida."
        )

    if registrada.data.tags.get("mlflow.runName") != NOME_RUN:
        raise ValueError(
            "Run existente com nome diferente."
        )

    if not ARQUIVO_PREVISOES.is_file():
        raise ValueError(
            "Run anterior existe, mas suas previsoes "
            "locais nao foram encontradas."
        )

    if not ARQUIVO_CLASSIFICACAO.is_file():
        raise ValueError(
            "Relatorio de classificacao ausente."
        )

    print("\nRUN EXISTENTE REUTILIZADA:", run_id)
    print("NENHUM TREINAMENTO REPETIDO")

    return relatorio


def executar_aula():
    """Treina, avalia e registra o baseline no MLflow."""

    tracking_uri = configurar_tracking()

    anterior = verificar_run_anterior()

    if anterior is not None:
        print("\n===== RESULTADOS REGISTRADOS =====")
        print(
            json.dumps(
                anterior["metricas"],
                ensure_ascii=False,
                indent=2,
            )
        )
        return anterior

    (
        base,
        X_train,
        X_test,
        y_train,
        y_test,
    ) = carregar_dados()

    model_pipe = construir_pipeline()

    parametros = {
        "modelo": "LogisticRegression",
        "max_iter": 2000,
        "class_weight": "balanced",
        "test_size": 0.25,
        "cv_folds": 5,
        "random_state": RANDOM_STATE,
        "n_amostras": len(base),
        "n_features": X_train.shape[1],
        "scoring_cv": "roc_auc",
    }

    print("\n===== INICIANDO PRIMEIRA RUN =====")
    print("EXPERIMENTO:", EXPERIMENTO)
    print("NOME DA RUN:", NOME_RUN)
    print("TRACKING:", tracking_uri)

    with mlflow.start_run(
        run_name=NOME_RUN
    ) as run:

        (
            metricas,
            report,
            y_pred,
            y_proba,
        ) = calcular_metricas(
            model_pipe,
            X_train,
            X_test,
            y_train,
            y_test,
        )

        mlflow.log_params(parametros)
        mlflow.log_metrics(metricas)

        run_id = run.info.run_id
        experiment_id = run.info.experiment_id

    # Os arquivos desta aula sao salvos localmente,
    # mas nao sao logados como artefatos na run.
    # Esse registro sera estudado nas proximas aulas.

    cliente = novo_cliente()

    probabilidade = float(
        model_pipe.predict_proba(cliente)[0, 1]
    )

    classe_prevista = int(
        model_pipe.predict(cliente)[0]
    )

    previsoes = X_test.copy()
    previsoes[TARGET] = y_test.to_numpy()
    previsoes["probabilidade_inadimplente"] = y_proba
    previsoes["previsao_inadimplente"] = y_pred

    RESULTADOS.mkdir(
        parents=True,
        exist_ok=True,
    )

    previsoes.to_csv(
        ARQUIVO_PREVISOES,
        index=False,
        encoding="utf-8-sig",
    )

    ARQUIVO_CLASSIFICACAO.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    relatorio = {
        "aula": 4,
        "experimento": EXPERIMENTO,
        "nome_run": NOME_RUN,
        "run_id": run_id,
        "experiment_id": experiment_id,
        "tracking_uri": tracking_uri,
        "dataset": "Sintetico - Aula 03",
        "amostras_total": len(base),
        "amostras_treino": len(X_train),
        "amostras_teste": len(X_test),
        "parametros": parametros,
        "metricas": metricas,
        "simulacao_cliente": {
            "perfil": cliente.iloc[0].to_dict(),
            "probabilidade_inadimplencia": probabilidade,
            "classe_prevista": classe_prevista,
        },
        "modelo_treinado": True,
        "run_registrada": True,
        "artefatos_logados_na_run": False,
        "modelo_registrado_registry": False,
    }

    ARQUIVO_RELATORIO.write_text(
        json.dumps(
            relatorio,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("\n===== PRIMEIRA RUN REGISTRADA =====")
    print("RUN ID:", run_id)

    for nome, valor in metricas.items():
        print(f"{nome}: {valor:.6f}")

    print("\n===== CLIENTE SIMULADO =====")
    print(
        "Probabilidade estimada:",
        f"{probabilidade:.2%}",
    )
    print("Rotulo binario:", classe_prevista)

    print("\nRELATORIO:", ARQUIVO_RELATORIO)
    print("PREVISOES:", ARQUIVO_PREVISOES)

    return relatorio


if __name__ == "__main__":
    executar_aula()
