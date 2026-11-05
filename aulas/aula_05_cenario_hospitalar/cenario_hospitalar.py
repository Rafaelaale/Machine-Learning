from pathlib import Path
import csv
import json

PROJETO = Path(__file__).resolve().parents[2]
MATERIAL = PROJETO / "material_alura" / "AWSCienciaDeDados-main"
RESULTADOS = PROJETO / "resultados"

def localizar_dados():
    arquivos = list(MATERIAL.rglob("*.csv")) if MATERIAL.exists() else []
    return sorted(
        arquivos,
        key=lambda p: (0 if "heart" in p.name.lower() else 1, str(p))
    )

def analisar_csv(arquivo):
    with arquivo.open("r", encoding="utf-8-sig", newline="") as f:
        amostra = f.read(8192)
        f.seek(0)
        try:
            delimitador = csv.Sniffer().sniff(amostra, delimiters=",;").delimiter
        except csv.Error:
            delimitador = ","

        leitor = csv.DictReader(f, delimiter=delimitador)
        colunas = leitor.fieldnames or []
        total = 0
        classes = {"0": 0, "1": 0}

        alvo = next(
            (c for c in colunas if c.lower().replace("_", "") == "heartdisease"),
            None
        )

        for linha in leitor:
            total += 1
            if alvo and linha.get(alvo) in classes:
                classes[linha[alvo]] += 1

    return {
        "arquivo": str(arquivo),
        "registros": total,
        "colunas": colunas,
        "variavel_alvo": alvo,
        "distribuicao_alvo": classes if alvo else None
    }

def main():
    print("===== CENARIO: DOENCA CARDIACA =====")
    print("Objetivo: estudar classificacao binaria")
    print("Ambiente: 100% local e gratuito")

    arquivos = localizar_dados()
    print(f"\nArquivos CSV encontrados: {len(arquivos)}")

    analises = []

    for arquivo in arquivos:
        print(f"\nArquivo: {arquivo.name}")
        try:
            resultado = analisar_csv(arquivo)
            analises.append(resultado)
            print("Registros:", resultado["registros"])
            print("Colunas:", ", ".join(resultado["colunas"]))
            print("Alvo:", resultado["variavel_alvo"])

            if resultado["variavel_alvo"]:
                print("Distribuicao:", resultado["distribuicao_alvo"])
        except (OSError, UnicodeError, csv.Error) as erro:
            print("Nao foi possivel analisar:", erro)

    if not arquivos:
        print("\nNenhum CSV encontrado no material.")
        print("Na proxima etapa verificaremos o dataset da aula.")

    relatorio = {
        "aula": 5,
        "projeto": "Predicao de doenca cardiaca",
        "tipo_problema": "classificacao_binaria",
        "ambiente": "local",
        "servicos_aws_criados": 0,
        "arquivos_encontrados": len(arquivos),
        "analises": analises
    }

    RESULTADOS.mkdir(parents=True, exist_ok=True)
    destino = RESULTADOS / "aula_05_cenario_hospitalar.json"
    destino.write_text(
        json.dumps(relatorio, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    assert destino.exists()
    assert relatorio["servicos_aws_criados"] == 0

    print("\nRELATORIO:", destino)
    print("AULA 05 - CENARIO PREPARADO")

if __name__ == "__main__":
    main()
