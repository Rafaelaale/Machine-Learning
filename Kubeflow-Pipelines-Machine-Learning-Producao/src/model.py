from xgboost import XGBClassifier


def build_xgb_model(
    eta: float = 0.1,
    max_depth: int = 5,
    n_estimators: int = 200,
    scale_pos_weight: float | None = None,
    random_state: int = 42,
) -> XGBClassifier:

    return XGBClassifier(
        learning_rate=eta,
        max_depth=max_depth,
        n_estimators=n_estimators,
        scale_pos_weight=scale_pos_weight,
        eval_metric="aucpr",
        tree_method="hist",
        n_jobs=-1,
        random_state=random_state,
    )
