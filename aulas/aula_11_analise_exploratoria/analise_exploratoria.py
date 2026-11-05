from pathlib import Path
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.model_selection import train_test_split

BASE = Path(r"F:\AWS-CIENCIA-DE-DADOS-SEGURANCA-CUSTOS")
AULA = BASE / "aulas" / "aula_11_analise_exploratoria"
RESULTADOS = BASE / "resultados"
DADOS = BASE / "s3_local" / "hospital-dados" / "raw" / "heart.csv"
SPLIT = RESULTADOS / "aula_11_split"

CONTINUAS = ["Age", "RestingBP", "Cholesterol", "MaxHR", "Oldpeak"]
CATEGORICAS = ["ChestPainType", "Sex", "RestingECG", "ST_Slope"]
BINARIAS = ["FastingBS", "ExerciseAngina"]
TARGET = "HeartDisease"


def main():
    print("===== AULA 11 - ANALISE EXPLORATORIA =====")
    print("Modo: LOCAL - SEM CONEXAO AWS")

    if not DADOS.is_file():
        raise FileNotFoundError(DADOS)

    df = pd.read_csv(DADOS)

    assert df.shape == (918, 12)
    assert TARGET in df.columns
    assert df[TARGET].isin([0, 1]).all()

    print("\n===== INFORMACOES DO DATAFRAME =====")
    print("Dimensoes:", df.shape)
    print("Colunas:", list(df.columns))
    print("\nTipos:")
    print(df.dtypes.to_string())

    print("\n===== PRIMEIRAS CINCO LINHAS =====")
    print(df.head().to_string(index=False))

    print("\n===== ESTATISTICAS DESCRITIVAS =====")
    estatisticas = df[CONTINUAS].describe()
    print(estatisticas.to_string())

    print("\n===== QUALIDADE DOS DADOS =====")

    duplicatas = int(df.duplicated().sum())
    nulos = df.isna().sum().astype(int).to_dict()

    zeros = {
        "RestingBP": int((df["RestingBP"] == 0).sum()),
        "Cholesterol": int((df["Cholesterol"] == 0).sum()),
        "Oldpeak": int((df["Oldpeak"] == 0).sum())
    }

    print("Duplicatas:", duplicatas)
    print("Total de nulos:", sum(nulos.values()))
    print("Zeros encontrados:", zeros)
    print("Observacao: Oldpeak igual a zero nao e necessariamente invalido.")

    distribuicao = df[TARGET].value_counts().sort_index().to_dict()

    print("\n===== VARIAVEL ALVO =====")
    print("Sem doenca (0):", distribuicao.get(0, 0))
    print("Com doenca (1):", distribuicao.get(1, 0))

    print("\n===== GERANDO 12 GRAFICOS =====")

    plt.style.use("ggplot")
    fig, axs = plt.subplots(6, 2, figsize=(15, 27))
    axs = axs.flatten()

    cores = {0: "#3478bf", 1: "#d35a53"}

    for ax, coluna in zip(axs, df.columns):
        if coluna in CONTINUAS:
            for classe in (0, 1):
                valores = df.loc[df[TARGET] == classe, coluna]
                ax.hist(
                    valores,
                    bins=25,
                    alpha=0.6,
                    color=cores[classe],
                    label=f"HeartDisease={classe}"
                )
        elif coluna == TARGET:
            contagem = df[TARGET].value_counts().sort_index()
            ax.bar(
                [str(x) for x in contagem.index],
                contagem.values,
                color=[cores[int(x)] for x in contagem.index]
            )
        else:
            contagem = pd.crosstab(df[coluna], df[TARGET])
            contagem = contagem.reindex(columns=[0, 1], fill_value=0)

            categorias = contagem.index.astype(str).tolist()
            posicoes = range(len(categorias))

            ax.bar(
                posicoes,
                contagem[0].values,
                color=cores[0],
                label="HeartDisease=0"
            )
            ax.bar(
                posicoes,
                contagem[1].values,
                bottom=contagem[0].values,
                color=cores[1],
                label="HeartDisease=1"
            )
            ax.set_xticks(list(posicoes))
            ax.set_xticklabels(categorias, rotation=35)

        ax.set_title(coluna)
        ax.set_ylabel("Quantidade")
        if coluna != TARGET:
            ax.legend(fontsize=8)

    fig.suptitle(
        "Analise exploratoria - Heart Disease Dataset",
        fontsize=16
    )
    fig.tight_layout(rect=[0, 0, 1, 0.98])

    grafico = RESULTADOS / "aula_11_distribuicoes.png"
    fig.savefig(grafico, dpi=140, bbox_inches="tight")
    plt.close(fig)

    print("Grafico salvo:", grafico)

    print("\n===== DIVISAO TREINO / TESTE =====")

    X = df.drop(columns=[TARGET])
    y = df[TARGET]

    train_X, test_X, train_y, test_y = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y
    )

    assert len(train_X) == 688
    assert len(test_X) == 230
    assert set(train_X.index).isdisjoint(set(test_X.index))

    print("Treino:", train_X.shape)
    print("Teste:", test_X.shape)

    SPLIT.mkdir(parents=True, exist_ok=True)

    treino = train_X.copy()
    treino[TARGET] = train_y

    teste = test_X.copy()
    teste[TARGET] = test_y

    treino.to_csv(SPLIT / "treino.csv", index=False)
    teste.to_csv(SPLIT / "teste.csv", index=False)

    print("Arquivos salvos:", SPLIT)

    relatorio = {
        "aula": 11,
        "dataset": str(DADOS),
        "total_registros": len(df),
        "colunas": list(df.columns),
        "variavel_alvo": TARGET,
        "duplicatas": duplicatas,
        "valores_nulos": nulos,
        "zeros_investigados": zeros,
        "distribuicao_alvo": {
            str(k): int(v) for k, v in distribuicao.items()
        },
        "estatisticas_continuas": estatisticas.to_dict(),
        "treino": len(treino),
        "teste": len(teste),
        "preprocessamento_aplicado": False,
        "recursos_aws_criados": 0
    }

    arquivo = RESULTADOS / "aula_11_eda.json"

    arquivo.write_text(
        json.dumps(relatorio, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    assert grafico.is_file()
    assert (SPLIT / "treino.csv").is_file()
    assert (SPLIT / "teste.csv").is_file()

    print("\n===== VALIDACAO FINAL =====")
    print("TESTES: 5/5 APROVADOS")
    print("RELATORIO:", arquivo)
    print("GRAFICO:", grafico)
    print("AULA 11 - CONCLUIDA")


if __name__ == "__main__":
    main()
