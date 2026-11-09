from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.metrics import (
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
)

from src.features import (
    build_features,
    split_train_val_test,
    to_arrays,
)

from src.model import build_xgb_model


@dataclass
class TrainResult:
    model_path: str
    val_metrics: dict
    test_metrics: dict


def evaluate(
    model,
    X: np.ndarray,
    y: np.ndarray,
    threshold: float = 0.5,
) -> dict:

    probs = model.predict_proba(X)[:, 1]
    preds = (probs > threshold).astype(int)

    return {
        "precision": precision_score(y, preds, zero_division=0),
        "recall": recall_score(y, preds, zero_division=0),
        "f1": f1_score(y, preds, zero_division=0),
        "pr_auc": average_precision_score(y, probs),
    }


def train(
    df: pd.DataFrame,
    eta: float = 0.1,
    max_depth: int = 5,
    n_estimators: int = 200,
    model_out: str = "model.ubj",
) -> TrainResult:

    train_df, val_df, test_df = split_train_val_test(df)

    X_train, y_train = to_arrays(train_df)
    X_val, y_val = to_arrays(val_df)
    X_test, y_test = to_arrays(test_df)

    scale = float(
        (y_train == 0).sum() /
        max((y_train == 1).sum(), 1)
    )

    model = build_xgb_model(
        eta=eta,
        max_depth=max_depth,
        n_estimators=n_estimators,
        scale_pos_weight=scale,
    )

    model.fit(
        X_train,
        y_train,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )

    val_metrics = evaluate(model, X_val, y_val)
    test_metrics = evaluate(model, X_test, y_test)

    out_path = Path(model_out)

    if out_path.suffix not in {".ubj", ".json", ".bst"}:
        out_path = out_path.with_suffix(".ubj")

    out_path.parent.mkdir(parents=True, exist_ok=True)

    if out_path.exists():
        raise FileExistsError(
            f"Modelo existente preservado: {out_path}"
        )

    model.save_model(str(out_path))

    print(f"val_pr_auc={val_metrics['pr_auc']:.4f}")

    return TrainResult(
        model_path=str(out_path),
        val_metrics=val_metrics,
        test_metrics=test_metrics,
    )


def train_from_csv(
    csv_path: str,
    eta: float = 0.1,
    max_depth: int = 5,
    n_estimators: int = 200,
    model_out: str = "model.ubj",
) -> TrainResult:

    df = build_features(pd.read_csv(csv_path))

    return train(
        df,
        eta=eta,
        max_depth=max_depth,
        n_estimators=n_estimators,
        model_out=model_out,
    )