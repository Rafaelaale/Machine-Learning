import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split


FEATURE_COLUMNS = (
    [f"V{i}" for i in range(1, 29)]
    + ["Amount", "hour_of_day", "segment"]
)

TARGET_COLUMN = "Class"

SEGMENT_CODES = {
    "low": 0,
    "medium": 1,
    "high": 2,
}


def add_hour_of_day(df: pd.DataFrame) -> pd.DataFrame:
    return df.assign(
        hour_of_day=(df["Time"] % 86_400) / 3_600
    )


def add_segment(df: pd.DataFrame) -> pd.DataFrame:
    q1, q3 = df["Amount"].quantile([0.25, 0.75])

    bins = [-float("inf"), q1, q3, float("inf")]

    cat = pd.cut(
        df["Amount"],
        bins=bins,
        labels=["low", "medium", "high"],
    )

    codes = cat.map(SEGMENT_CODES).astype("int8")

    return df.assign(segment=codes)


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    if "hour_of_day" not in df.columns:
        df = add_hour_of_day(df)

    if "segment" not in df.columns:
        df = add_segment(df)

    return df


def split_train_val_test(
    df: pd.DataFrame,
    val_size: float = 0.2,
    test_size: float = 0.2,
    stratify_col: str = "Class",
    seed: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:

    trainval, test = train_test_split(
        df,
        test_size=test_size,
        stratify=df[stratify_col],
        random_state=seed,
    )

    val_fraction = val_size / (1 - test_size)

    train, val = train_test_split(
        trainval,
        test_size=val_fraction,
        stratify=trainval[stratify_col],
        random_state=seed,
    )

    return train, val, test


def to_arrays(
    df: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray]:

    X = df[FEATURE_COLUMNS].to_numpy(dtype=np.float32)
    y = df[TARGET_COLUMN].to_numpy(dtype=np.float32)

    return X, y