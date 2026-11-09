import argparse

import pandas as pd

from src.features import build_features
from src.train import train


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("--eta", type=float, required=True)
    parser.add_argument("--max-depth", type=int, required=True)
    parser.add_argument("--n-estimators", type=int, required=True)
    parser.add_argument("--csv", type=str, default="/data/creditcard.csv")
    parser.add_argument("--model_out", type=str, default="/tmp/model.ubj")

    args = parser.parse_args()

    df = pd.read_csv(args.csv)
    df = build_features(df)

    result = train(
        df,
        eta=args.eta,
        max_depth=args.max_depth,
        n_estimators=args.n_estimators,
        model_out=args.model_out,
    )

    print("TREINAMENTO KATIB CONCLUIDO")
    print(f"val_pr_auc={result.val_metrics['pr_auc']:.4f}")


if __name__ == "__main__":
    main()
