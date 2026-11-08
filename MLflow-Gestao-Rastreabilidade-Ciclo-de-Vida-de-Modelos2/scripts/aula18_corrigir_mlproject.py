from pathlib import Path
import yaml

arquivo = Path("MLproject")

conteudo = arquivo.read_text(
    encoding="utf-8-sig"
)

antigo = ".venv/Scripts/python.exe -m src."
novo = "python -m src."

if antigo in conteudo:
    conteudo = conteudo.replace(antigo, novo)

    arquivo.write_text(
        conteudo,
        encoding="utf-8",
    )

    print("CAMINHOS WINDOWS CORRIGIDOS")
else:
    print("CAMINHOS JA CORRIGIDOS")

config = yaml.safe_load(
    arquivo.read_text(encoding="utf-8")
)

entrypoints = config["entry_points"]

for nome in ("prepare", "train", "evaluate", "pipeline"):
    if nome not in entrypoints:
        raise RuntimeError(
            f"Entry point ausente: {nome}"
        )

    comando = entrypoints[nome]["command"].strip()

    if not comando.startswith("python -m src."):
        raise RuntimeError(
            f"Comando incorreto em {nome}: {comando}"
        )

    print(f"{nome.upper()}: {comando}")

print("MLPROJECT VALIDADO")