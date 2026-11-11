from pathlib import Path
import json
import sys

fonte = Path(sys.argv[1])

arquivos = {
    "Eventos Bronze": "aula_1/base_bronze_eventos.csv",
    "Dimensao de produtos": "aula_1/base_dim_produtos.csv",
    "Notebook de ingestao": "aula_1/aula_1_4_projeto_ingestao.ipynb",
    "Pipeline de ingestao": "aula_6/pipeline/01_ingestao_dados.py",
    "Pre-processamento": "aula_6/pipeline/02_pre_processamento.py",
    "Treinamento": "aula_6/pipeline/03_treinamento_modelo.py",
    "Configuracao Databricks": "databricks.yml",
}

print("\n===== AUDITORIA DA ARQUITETURA =====")

encontrados = 0

for descricao, relativo in arquivos.items():
    caminho = fonte / relativo

    if caminho.is_file():
        encontrados += 1
        print(f"OK: {descricao}")
    else:
        print(f"AUSENTE: {descricao}")

print("\n===== CAMADAS MEDALLION =====")

pipeline = fonte / "aula_6/pipeline/01_ingestao_dados.py"

if pipeline.is_file():
    texto = pipeline.read_text(encoding="utf-8-sig")

    for camada in ["bronze", "silver", "gold"]:
        if camada in texto.lower():
            print(f"IDENTIFICADA: {camada.upper()}")
        else:
            print(f"REVISAR: {camada.upper()}")

    if "workspace.silver.tabela_eventos_silver" in texto:
        print("ATENCAO: referencia fixa do instrutor identificada.")

print("\n===== RESULTADO =====")
print(f"ARQUIVOS ENCONTRADOS: {encontrados}/{len(arquivos)}")
print("Auditoria estatica, sem executar Databricks.")
print("Nenhum arquivo modificado.")

if encontrados != len(arquivos):
    sys.exit(1)