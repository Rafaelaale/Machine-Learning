"""Aula 12: testes automatizados do pacote de churn.

Abrangencia:
- leitura e validacao de arquivos;
- transformacao de datas;
- tratamento de dados ausentes;
- codificacao de churn;
- engenharia de atributos;
- codificacao categorica;
- integridade e reproducibilidade;
- execucao completa do pipeline.
"""

from pathlib import Path

import pandas as pd
import pytest

from pre_processamento import PreProcessamento


@pytest.fixture
def dados_csv(tmp_path):
    """Cria um CSV de clientes em diretorio temporario."""
    clientes = pd.DataFrame({
        "customer_id": [1, 2, 3, 4],
        "signup_date": [
            "2022-01-01",
            "2022-01-15",
            "data_invalida",
            "2022-03-01",
        ],
        "last_purchase_date": [
            "2022-01-20",
            "2022-02-01",
            None,
            "2022-03-15",
        ],
        "product_category": [
            "eletronico",
            None,
            "livros",
            "casa",
        ],
        "total_spent": [1000.0, 500.0, 300.0, 150.0],
        "num_orders": [10, 5, 0, 3],
        "cancel_date": [None, None, None, None],
        "data_ingestion": [
            "2022-02-05",
            "2022-02-10",
            "2022-03-10",
            "2022-03-20",
        ],
        "city": ["Sao Paulo", None, "Salvador", "Recife"],
        "payment_method": ["pix", "boleto", None, "credito"],
        "product_id": ["A1", "B2", "C3", "D4"],
        "churn": ["no", "yes", "desconhecido", "sim"],
        "days_since_last_purchase": [10, None, 30, 0],
    })

    caminho = tmp_path / "clientes_teste.csv"
    clientes.to_csv(caminho, index=False)

    return caminho


@pytest.fixture
def processador(dados_csv):
    """Fornece uma instancia independente por teste."""
    return PreProcessamento(str(dados_csv))


def test_01_instancia_sem_dados(processador):
    assert processador.df is None


def test_02_carregar_csv(processador):
    processador.carregar_dados()

    assert len(processador.df) == 4
    assert "churn" in processador.df.columns


def test_03_arquivo_inexistente(tmp_path):
    caminho = tmp_path / "nao_existe.csv"
    processador = PreProcessamento(str(caminho))

    with pytest.raises(FileNotFoundError):
        processador.carregar_dados()


def test_04_coluna_obrigatoria_ausente(dados_csv):
    clientes = pd.read_csv(dados_csv)
    clientes = clientes.drop(columns=["churn"])
    clientes.to_csv(dados_csv, index=False)

    processador = PreProcessamento(str(dados_csv))

    with pytest.raises(ValueError, match="churn"):
        processador.carregar_dados()


def test_05_metodo_sem_carregamento(processador):
    with pytest.raises(RuntimeError):
        processador.tratar_datas()


def test_06_colunas_de_data(processador):
    processador.carregar_dados()
    processador.tratar_datas()

    for coluna in (
        "signup_date",
        "last_purchase_date",
        "cancel_date",
        "data_ingestion",
    ):
        assert pd.api.types.is_datetime64_any_dtype(
            processador.df[coluna]
        )


def test_07_data_invalida_converte_para_nat(processador):
    processador.carregar_dados()
    processador.tratar_datas()

    assert pd.isna(processador.df.loc[2, "signup_date"])


def test_08_colunas_de_data_opcionais(dados_csv):
    dados = pd.read_csv(dados_csv)

    dados = dados.drop(
        columns=["cancel_date", "data_ingestion"]
    )

    dados.to_csv(dados_csv, index=False)

    processador = PreProcessamento(str(dados_csv))
    processador.carregar_dados()
    processador.tratar_datas()

    assert pd.api.types.is_datetime64_any_dtype(
        processador.df["signup_date"]
    )


def test_09_preenchimento_nulos(processador):
    processador.carregar_dados()
    processador.preencher_nulos()

    for coluna in (
        "city",
        "product_category",
        "payment_method",
        "days_since_last_purchase",
    ):
        assert processador.df[coluna].isna().sum() == 0


def test_10_mediana_dos_dias(processador):
    processador.carregar_dados()
    processador.preencher_nulos()

    # Mediana de 0, 10 e 30 = 10.
    assert processador.df.loc[1, "days_since_last_purchase"] == 10


def test_11_sem_dias_validos(dados_csv):
    dados = pd.read_csv(dados_csv)
    dados["days_since_last_purchase"] = None
    dados.to_csv(dados_csv, index=False)

    processador = PreProcessamento(str(dados_csv))
    processador.carregar_dados()

    with pytest.raises(ValueError, match="mediana"):
        processador.preencher_nulos()


@pytest.mark.parametrize(
    ("rotulo", "esperado"),
    [
        ("yes", 1),
        ("no", 0),
        ("sim", 1),
        ("nao", 0),
        ("1", 1),
        ("0", 0),
    ],
)
def test_12_codificacao_churn(rotulo, esperado, dados_csv):
    dados = pd.read_csv(dados_csv)
    dados.loc[0, "churn"] = rotulo
    dados.to_csv(dados_csv, index=False)

    processador = PreProcessamento(str(dados_csv))
    processador.carregar_dados()
    processador.codificar_churn()

    assert processador.df.loc[0, "churn"] == esperado


def test_13_churn_desconhecido_preservado(processador):
    processador.carregar_dados()
    processador.codificar_churn()

    assert pd.isna(processador.df.loc[2, "churn"])


def test_14_churn_conhecido_binario(processador):
    processador.carregar_dados()
    processador.codificar_churn()

    conhecidos = processador.df["churn"].dropna()

    assert set(conhecidos.unique()).issubset({0, 1})


def test_15_calculo_fidelidade(processador):
    processador.carregar_dados()
    processador.preencher_nulos()
    processador.criar_colunas_derivadas()

    assert processador.df.loc[0, "fidelidade"] == pytest.approx(
        10 / 11
    )


def test_16_calculo_score_gasto(processador):
    processador.carregar_dados()
    processador.preencher_nulos()
    processador.criar_colunas_derivadas()

    assert processador.df.loc[0, "score_gasto"] == 10000


def test_17_zero_dias_sem_divisao_por_zero(processador):
    processador.carregar_dados()
    processador.preencher_nulos()
    processador.criar_colunas_derivadas()

    assert processador.df.loc[3, "fidelidade"] == 3


@pytest.mark.parametrize(
    ("coluna", "valor"),
    [
        ("total_spent", -100),
        ("num_orders", -1),
        ("days_since_last_purchase", -5),
    ],
)
def test_18_rejeitar_valores_negativos(
    coluna,
    valor,
    dados_csv,
):
    dados = pd.read_csv(dados_csv)
    dados.loc[0, coluna] = valor
    dados.to_csv(dados_csv, index=False)

    processador = PreProcessamento(str(dados_csv))
    processador.carregar_dados()
    processador.preencher_nulos()

    with pytest.raises(ValueError, match="negativos"):
        processador.criar_colunas_derivadas()


def test_19_rejeitar_valor_numerico_invalido(dados_csv):
    dados = pd.read_csv(dados_csv)
    dados["total_spent"] = dados["total_spent"].astype(object)
    dados.loc[0, "total_spent"] = "valor_invalido"
    dados.to_csv(dados_csv, index=False)

    processador = PreProcessamento(str(dados_csv))
    processador.carregar_dados()
    processador.preencher_nulos()

    with pytest.raises((ValueError, TypeError)):
        processador.criar_colunas_derivadas()


def test_20_one_hot_encoding(processador):
    processador.carregar_dados()
    processador.preencher_nulos()
    processador.codificar_categoricas()

    assert "product_category_eletronico" in processador.df.columns
    assert "payment_method_pix" in processador.df.columns


def test_21_one_hot_binario(processador):
    processador.carregar_dados()
    processador.preencher_nulos()
    processador.codificar_categoricas()

    colunas = [
        coluna
        for coluna in processador.df.columns
        if coluna.startswith(
            ("product_category_", "payment_method_")
        )
    ]

    assert colunas

    valores = set(
        processador.df[colunas].to_numpy().ravel()
    )

    assert valores.issubset({0, 1})


def test_22_salvar_sem_carregamento(processador, tmp_path):
    saida = tmp_path / "saida.csv"

    with pytest.raises(RuntimeError):
        processador.salvar_dados(str(saida))


def test_23_pipeline_completo(processador, tmp_path):
    saida = tmp_path / "processados" / "clientes.csv"

    processador.executar_pipeline(str(saida))

    assert saida.is_file()

    resultado = pd.read_csv(saida)

    assert len(resultado) == 4
    assert "fidelidade" in resultado.columns
    assert "score_gasto" in resultado.columns
    assert "payment_method_pix" in resultado.columns
    assert resultado["churn"].isna().sum() == 1


def test_24_preserva_csv_original(processador, dados_csv, tmp_path):
    conteudo_original = Path(dados_csv).read_bytes()

    processador.executar_pipeline(
        str(tmp_path / "saida.csv")
    )

    assert dados_csv.read_bytes() == conteudo_original


def test_25_execucao_reproduzivel(processador, tmp_path):
    saida = tmp_path / "saida.csv"

    processador.executar_pipeline(str(saida))
    primeira = saida.read_bytes()

    processador.executar_pipeline(str(saida))
    segunda = saida.read_bytes()

    assert primeira == segunda


def test_26_categorias_opcionais_ausentes(dados_csv, tmp_path):
    dados = pd.read_csv(dados_csv)
    dados = dados.drop(
        columns=["product_category", "payment_method"]
    )
    dados.to_csv(dados_csv, index=False)

    processador = PreProcessamento(str(dados_csv))
    saida = tmp_path / "saida.csv"

    processador.executar_pipeline(str(saida))

    resultado = pd.read_csv(saida)

    assert "fidelidade" in resultado.columns
    assert "score_gasto" in resultado.columns
    assert not any(
        coluna.startswith("payment_method_")
        for coluna in resultado.columns
    )
