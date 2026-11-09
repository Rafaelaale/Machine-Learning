import json
import os
from pathlib import Path

import pandas as pd

from src.features import build_features
from src.train import train


def _read(path: str) -> pd.DataFrame:
    if path.endswith(".parquet"):
        return pd.read_parquet(path)
    return pd.read_csv(path)


def main() -> None:
    csv = os.environ.get("CSV", "/data/creditcard.csv")
    models_dir = os.environ.get("MODELS_DIR", "/models")

    eta = float(os.environ.get("ETA", "0.2430296138044891"))
    max_depth = int(os.environ.get("MAX_DEPTH", "5"))
    n_estimators = int(os.environ.get("N_ESTIMATORS", "194"))

    output_dir = Path(models_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    model_out = output_dir / "model.ubj"
    metrics_out = output_dir / "metrics.json"

    print("INICIANDO TREINAMENTO XGBOOST", flush=True)
    print(f"dataset={csv}", flush=True)
    print(f"eta={eta}", flush=True)
    print(f"max_depth={max_depth}", flush=True)
    print(f"n_estimators={n_estimators}", flush=True)

    df = pd.read_parquet(csv) if csv.lower().endswith(".parquet") else build_features(_read(csv))

    result = train(
        df,
        eta=eta,
        max_depth=max_depth,
        n_estimators=n_estimators,
        model_out=str(model_out),
    )

    metrics = {
        "val_pr_auc": float(result.val_metrics["pr_auc"]),
        "val_recall": float(result.val_metrics["recall"]),
        "test_pr_auc": float(result.test_metrics["pr_auc"]),
    }

    metrics_out.write_text(
        json.dumps(metrics, indent=2),
        encoding="utf-8",
    )

    if not model_out.is_file():
        raise RuntimeError("Arquivo do modelo nao foi gerado.")

    print(f"model_path={model_out}", flush=True)
    print(f"metrics_path={metrics_out}", flush=True)
    print(f"val_pr_auc={metrics['val_pr_auc']:.4f}", flush=True)
    print(f"test_pr_auc={metrics['test_pr_auc']:.4f}", flush=True)
    print("TREINAMENTO FINALIZADO", flush=True)


if __name__ == "__main__":
    main()
