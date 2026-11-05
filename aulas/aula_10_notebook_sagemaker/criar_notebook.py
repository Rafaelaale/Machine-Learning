from pathlib import Path
import json
import csv
import importlib.util

PROJETO = Path(r"F:\AWS-CIENCIA-DE-DADOS-SEGURANCA-CUSTOS")
AULA = PROJETO / "aulas" / "aula_10_notebook_sagemaker"
DADOS = PROJETO / "s3_local" / "hospital-dados" / "raw" / "heart.csv"
DESTINO = AULA / "modelo_heart_disease.ipynb"

def markdown(texto):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": texto.splitlines(keepends=True)
    }

def codigo(texto):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": texto.splitlines(keepends=True)
    }

celulas = [
    markdown(
        "# Aula 10 - Notebook Heart Disease\n"
        "Laboratorio local equivalente ao SageMaker Notebook.\n"
        "Objetivo: preparar o ambiente para analise exploratoria.\n"
        "Nenhum recurso AWS sera utilizado."
    ),
    codigo(
        "import sys\n"
        "import pandas as pd\n"
        "import numpy as np\n"
        "print('Python:', sys.version.split()[0])\n"
        "print('Pandas:', pd.__version__)\n"
        "print('NumPy:', np.__version__)"
    ),
    codigo(
        "from pathlib import Path\n"
        "arquivo = Path("
        "r'F:\\AWS-CIENCIA-DE-DADOS-SEGURANCA-CUSTOS"
        "\\s3_local\\hospital-dados\\raw\\heart.csv')\n"
        "assert arquivo.exists(), 'Dataset nao encontrado'\n"
        "df = pd.read_csv(arquivo)\n"
        "print('Dimensoes:', df.shape)\n"
        "display(df.head())"
    ),
    codigo(
        "assert df.shape == (918, 12)\n"
        "assert 'HeartDisease' in df.columns\n"
        "print('Dataset validado: 918 registros e 12 colunas')\n"
        "print('Tipos de dados:')\n"
        "display(df.dtypes.to_frame('tipo'))"
    ),
    markdown(
        "## Proxima aula\n"
        "Explorar valores ausentes, distribuicoes e relacoes "
        "entre variaveis antes de treinar o modelo.\n\n"
        "**Uso exclusivamente educativo:** as previsoes "
        "nao devem orientar decisoes clinicas."
    )
]

notebook = {
    "cells": celulas,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 5
}

AULA.mkdir(parents=True, exist_ok=True)

DESTINO.write_text(
    json.dumps(notebook, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

with DADOS.open("r", encoding="utf-8-sig", newline="") as arquivo:
    leitor = csv.DictReader(arquivo)
    total = sum(1 for _ in leitor)

assert total == 918
assert len(celulas) == 5
assert json.loads(DESTINO.read_text(encoding="utf-8"))["nbformat"] == 4

print("===== VALIDACAO DA AULA 10 =====")
print("Dataset:", total, "registros")
print("Celulas do notebook:", len(celulas))
print("Pandas disponivel:", importlib.util.find_spec("pandas") is not None)
print("Jupyter disponivel:", importlib.util.find_spec("jupyter") is not None)
print("NOTEBOOK:", DESTINO)
print("TESTES: 3/3 APROVADOS")
print("AULA 10 - NOTEBOOK PREPARADO")
