from pathlib import Path
import json
import csv
import sys

root = Path(__file__).resolve().parents[1]
fonte = root / "material-alura/6123-alura-ml-databricks"
relatorio = root / "relatorios/auditoria_treinamento_aula3.txt"

notebooks = [
    "aula_3/aula_3_2_treinamento_modelos.ipynb",
    "aula_3/aula_3_3_SparkML_Hyperopt_Optuna.ipynb",
    "aula_3/aula_3_4_projeto_modelos.ipynb",
]

linhas = ["AUDITORIA - TREINAMENTO DE MODELOS", ""]

print("\n===== AUDITORIA DOS NOTEBOOKS ALURA =====")

for relativo in notebooks:

    caminho = fonte / relativo

    if not caminho.is_file():
        raise FileNotFoundError(caminho)

    notebook = json.loads(
        caminho.read_text(encoding="utf-8-sig")
    )

    celulas = notebook["cells"]

    quantidade_codigo = sum(
        c["cell_type"] == "code"
        for c in celulas
    )

    mensagem = (
        f"{caminho.name}: "
        f"{len(celulas)} celulas, "
        f"{quantidade_codigo} de codigo"
    )

    print("VALIDADO:", mensagem)
    linhas.append(mensagem)

iris = fonte / "aula_1/iris_dataset.csv"

with iris.open(
    encoding="utf-8-sig",
    newline=""
) as arquivo:
    dados = list(csv.DictReader(arquivo))

if len(dados) != 150:
    raise RuntimeError("Iris diferente do esperado")

print("DATASET IRIS: 150 REGISTROS")
linhas.append("Dataset Iris: 150 registros")

notebook_projeto = json.loads(
    (fonte / notebooks[2]).read_text(
        encoding="utf-8-sig"
    )
)

codigo_projeto = "\n".join(
    "".join(c["source"])
    for c in notebook_projeto["cells"]
    if c["cell_type"] == "code"
)

anterior = root / (
    "notebooks/aula_02_feature_store/"
    "04_features_temporais_ecommerce.py"
)

print("\n===== PENDENCIAS ANTECIPADAS =====")

avisos = []

if anterior.is_file():
    codigo_anterior = anterior.read_text(
        encoding="utf-8-sig"
    )

    if (
        '"timestamp_registro"' in codigo_anterior
        and 'primary_keys=["id_usuario", "dia_prtc"]'
        in codigo_projeto
    ):
        avisos.append(
            "Chaves temporais divergentes: "
            "timestamp_registro x dia_prtc."
        )

if "train_test_split(X, y, test_size=0.2" in codigo_projeto:
    avisos.append(
        "Projeto usa divisao aleatoria; "
        "avaliar separacao cronologica para e-commerce."
    )

if '.write.mode("overwrite")' in codigo_projeto:
    avisos.append(
        "Notebook original contem gravacao overwrite. "
        "Nao executar sem revisar a tabela de destino."
    )

avisos.append(
    "FeatureLookup e Model Registry dependem de "
    "tabelas, permissoes e recursos no Databricks."
)

for aviso in avisos:
    print("ATENCAO:", aviso)
    linhas.append("ATENCAO: " + aviso)

linhas += [
    "",
    "Material original preservado.",
    "Nenhum treinamento executado na nuvem.",
    "Nenhuma publicacao realizada."
]

relatorio.write_text(
    "\n".join(linhas) + "\n",
    encoding="utf-8"
)

print("\n===== AUDITORIA LOCAL CONCLUIDA =====")
print("NOTEBOOKS ALURA: 3/3")
print("IRIS: 150")
print("RELATORIO:", relatorio)