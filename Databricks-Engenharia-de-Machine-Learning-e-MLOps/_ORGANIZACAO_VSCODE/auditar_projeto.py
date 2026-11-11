from __future__ import annotations

import ast
import csv
import hashlib
import json
import os
import re
import sys

from collections import defaultdict
from datetime import datetime
from pathlib import Path

projeto = Path(sys.argv[1]).resolve()
aulas = projeto / "aulas"
saida = projeto / "_ORGANIZACAO_VSCODE"

saida.mkdir(exist_ok=True)

ignorar = {
    ".git",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".ipynb_checkpoints",
    "__pycache__",
    "node_modules",
    "site-packages",
    "build",
    "dist",
    "_ORGANIZACAO_VSCODE",
}

print("\n===== 2. INVENTARIANDO ARQUIVOS =====")

arquivos = []

for raiz, diretorios, nomes in os.walk(
    projeto, followlinks=False
):
    diretorios[:] = sorted(
        nome
        for nome in diretorios
        if nome not in ignorar
        and not nome.startswith(".venv")
        and nome != "venv"
        and not (Path(raiz) / nome).is_symlink()
    )

    for nome in nomes:
        caminho = Path(raiz) / nome

        try:
            if not caminho.is_file() or caminho.is_symlink():
                continue

            info = caminho.stat()

            arquivos.append({
                "caminho": caminho.relative_to(
                    projeto
                ).as_posix(),
                "extensao": caminho.suffix.lower(),
                "bytes": info.st_size,
                "modificado": datetime.fromtimestamp(
                    info.st_mtime
                ).strftime("%Y-%m-%d %H:%M"),
            })

        except (OSError, PermissionError):
            pass

arquivos.sort(key=lambda x: x["caminho"].lower())

inventario = saida / "INVENTARIO.csv"

with inventario.open(
    "w", newline="", encoding="utf-8-sig"
) as arquivo:
    escritor = csv.DictWriter(
        arquivo,
        fieldnames=[
            "caminho",
            "extensao",
            "bytes",
            "modificado",
        ],
        delimiter=";",
    )

    escritor.writeheader()
    escritor.writerows(arquivos)

print("ARQUIVOS INVENTARIADOS:", len(arquivos))


print("\n===== 3. IDENTIFICANDO COPIAS IDENTICAS =====")

hashes = defaultdict(list)

extensoes = {
    ".py",
    ".yml",
    ".yaml",
    ".ipynb",
    ".sql",
    ".ps1",
    ".md",
    ".json",
}

for item in arquivos:
    if item["extensao"] not in extensoes:
        continue

    if item["bytes"] > 3 * 1024 * 1024:
        continue

    caminho = projeto / item["caminho"]

    try:
        resumo = hashlib.sha256(
            caminho.read_bytes()
        ).hexdigest()

        hashes[resumo].append(item["caminho"])

    except (OSError, PermissionError):
        pass

duplicados = {
    chave: nomes
    for chave, nomes in hashes.items()
    if len(nomes) > 1
}

with (
    saida / "ARQUIVOS_IDENTICOS.csv"
).open("w", newline="", encoding="utf-8-sig") as arquivo:

    escritor = csv.writer(
        arquivo,
        delimiter=";",
    )

    escritor.writerow([
        "hash_sha256",
        "caminho",
        "total_no_grupo",
    ])

    for resumo, nomes in sorted(duplicados.items()):
        for nome in nomes:
            escritor.writerow([
                resumo,
                nome,
                len(nomes),
            ])

print("GRUPOS DE COPIAS IDENTICAS:", len(duplicados))
print("NENHUMA COPIA FOI APAGADA")


print("\n===== 4. LOCALIZANDO BACKUPS E ARQUIVOS GRANDES =====")

temporarios = [
    item["caminho"]
    for item in arquivos
    if re.search(
        r"(?i)(\.download$|\.tmp$|\.bak$|"
        r"\.backup(?:_.*)?$|\.old$|\.orig$)",
        item["caminho"],
    )
]

grandes = sorted(
    (
        item
        for item in arquivos
        if item["bytes"] >= 10 * 1024 * 1024
    ),
    key=lambda x: x["bytes"],
    reverse=True,
)

print("BACKUPS E TEMPORARIOS:", len(temporarios))
print("ARQUIVOS GRANDES:", len(grandes))


print("\n===== 5. VERIFICANDO ESTRUTURA DAS AULAS =====")

esperadas = [
    ("05.02 - Drift", "aula_05_02_drift_aprimorado"),
    ("05.03 - Jobs", "aula_05_03_jobs"),
    ("05.04 - Alertas", "aula_05_04_alertas_locais"),
    ("05.05 - Retreino", "aula_05_05_retreino_local"),
    ("05.06 - DABs", "aula_05_06_iac_dabs"),
    ("06.01 - CI/CD", "aula_06_01_cicd_mlops"),
    ("06.02 - GitHub Actions", "aula_06_02_github_actions"),
    ("06.03 - Codigos produtivos", "aula_06_03_pipeline_final"),
    ("06.04 - Pipeline completo", "aula_06_04_pipeline_completo"),
    ("06.05 - Unity Catalog", "aula_06_05_unity_catalog_acessos"),
]

verificacoes = []
problemas = []

def verificar(nome, condicao, detalhe=""):
    estado = "OK" if condicao else "ATENCAO"

    verificacoes.append({
        "nome": nome,
        "estado": estado,
        "detalhe": detalhe,
    })

    if not condicao:
        problemas.append(f"{nome}: {detalhe}")

    print(f"{estado}: {nome}")

for titulo, pasta in esperadas:
    verificar(
        titulo,
        (aulas / pasta).is_dir(),
        f"aulas/{pasta}",
    )


print("\n===== 6. AUDITANDO O PIPELINE FINAL =====")

pipeline = aulas / "aula_06_04_pipeline_completo"

if pipeline.is_dir():
    pasta_notebooks = pipeline / "notebooks"

    notebooks = (
        sorted(pasta_notebooks.glob("0[1-7]_*.py"))
        if pasta_notebooks.is_dir()
        else []
    )

    verificar(
        "Sete notebooks da Aula 6.4",
        len(notebooks) == 7,
        f"Encontrados: {len(notebooks)}",
    )

    for notebook in notebooks:
        try:
            codigo = notebook.read_text(
                encoding="utf-8-sig"
            )

            linhas = [
                "pass"
                if linha.lstrip().startswith("%")
                else linha
                for linha in codigo.splitlines()
            ]

            ast.parse(
                "\n".join(linhas),
                filename=notebook.name,
            )

            print("SINTAXE OK:", notebook.name)

        except (SyntaxError, OSError, UnicodeError) as erro:
            problemas.append(
                f"Sintaxe {notebook.name}: {erro}"
            )

    try:
        import yaml

        caminho_jobs = pipeline / "resources/jobs.yml"
        caminho_bundle = pipeline / "databricks.yml"

        jobs = yaml.safe_load(
            caminho_jobs.read_text(
                encoding="utf-8-sig"
            )
        )

        bundle = yaml.safe_load(
            caminho_bundle.read_text(
                encoding="utf-8-sig"
            )
        )

        tarefas = jobs["resources"]["jobs"][
            "pipeline_completo_mlops"
        ]["tasks"]

        verificar(
            "Bundle e oito tarefas",
            len(tarefas) == 8
            and len(bundle["targets"]) == 3,
            f"{len(tarefas)} tarefas",
        )

        for tarefa in tarefas:
            especificacao = tarefa.get("notebook_task")

            if not especificacao:
                continue

            caminho = (
                caminho_jobs.parent
                / especificacao["notebook_path"]
            ).resolve()

            if not caminho.is_file():
                problemas.append(
                    f"Notebook ausente: {caminho}"
                )

    except ImportError:
        problemas.append("PyYAML indisponivel neste Python")

    except Exception as erro:
        problemas.append(f"YAML da Aula 6.4: {erro}")

    try:
        dados = json.loads(
            (
                pipeline
                / "resultados/AUDITORIA_FINAL.json"
            ).read_text(encoding="utf-8-sig")
        )

        verificar(
            "Auditoria anterior da Aula 6.4",
            dados.get("tarefas") == 8
            and dados.get("notebooks") == 7
            and len(dados.get("cenarios", {})) == 6,
            "8 tarefas, 7 notebooks e 6 cenarios",
        )

    except (OSError, ValueError) as erro:
        problemas.append(
            f"Auditoria 6.4 nao legivel: {erro}"
        )


print("\n===== 7. CONFERINDO AUDITORIAS ANTERIORES =====")

arquivo_65 = (
    aulas
    / "aula_06_05_unity_catalog_acessos"
    / "resultados/AUDITORIA_UNITY_CATALOG.json"
)

try:
    dados = json.loads(
        arquivo_65.read_text(encoding="utf-8-sig")
    )

    verificar(
        "Aula 6.5 - Acessos",
        dados.get("validacoes") == 8,
        "Oito testes de permissoes",
    )

except (OSError, ValueError) as erro:
    problemas.append(f"Auditoria 6.5: {erro}")


arquivo_62 = (
    aulas
    / "aula_06_02_github_actions"
    / "resultados/RELATORIO_EXECUCAO.json"
)

try:
    dados = json.loads(
        arquivo_62.read_text(encoding="utf-8-sig")
    )

    encontrados = (
        {
            item.get("ambiente")
            for item in dados
            if isinstance(item, dict)
        }
        if isinstance(dados, list)
        else set()
    )

    verificar(
        "Aula 6.2 - Tres ambientes",
        isinstance(dados, list)
        and len(dados) == 3
        and encontrados == {"dev", "stage", "prod"},
        "DEV, STAGE e PROD",
    )

except (OSError, ValueError, TypeError) as erro:
    problemas.append(f"Auditoria 6.2: {erro}")


print("\n===== 8. ORGANIZANDO VISUALIZACAO DO VSCODE =====")

configuracoes = {
    "files.exclude": {
        "**/.venv*": True,
        "**/venv": True,
        "**/__pycache__": True,
        "**/.pytest_cache": True,
        "**/.mypy_cache": True,
        "**/.ruff_cache": True,
        "**/.ipynb_checkpoints": True,
        "**/node_modules": True,
        "**/*.download": True,
        "**/*.bak": True,
    },
    "search.exclude": {
        "**/.venv*": True,
        "**/venv": True,
        "**/node_modules": True,
        "**/__pycache__": True,
    },
}

workspace_aulas = projeto / "VISUALIZACAO_AULAS.code-workspace"

conteudo_aulas = {
    "folders": [
        {
            "name": "AULAS - DATABRICKS",
            "path": "aulas",
        },
        {
            "name": "INDICE E AUDITORIA",
            "path": "_ORGANIZACAO_VSCODE",
        },
    ],
    "settings": configuracoes,
}

if not workspace_aulas.exists():
    workspace_aulas.write_text(
        json.dumps(
            conteudo_aulas,
            indent=2,
            ensure_ascii=False,
        ) + "\n",
        encoding="utf-8",
    )

workspace_geral = projeto / "VISAO_GERAL.code-workspace"

if not workspace_geral.exists():
    workspace_geral.write_text(
        json.dumps({
            "folders": [
                {
                    "name": "PROJETO COMPLETO",
                    "path": ".",
                }
            ],
            "settings": configuracoes,
        }, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


print("\n===== 9. CRIANDO INDICE DE AULAS =====")

indice = [
    "# Indice do Projeto Databricks MLOps",
    "",
    "As pastas originais permanecem preservadas.",
    "",
    "| Aula | Diretorio | Situacao |",
    "|---|---|---|",
]

for titulo, pasta in esperadas:
    existe = (aulas / pasta).is_dir()

    indice.append(
        f"| {titulo} | `aulas/{pasta}` | "
        f"{'Encontrada' if existe else 'NAO ENCONTRADA'} |"
    )

indice.extend([
    "",
    "## Arquivos de organizacao",
    "",
    "- `INVENTARIO.csv`: inventario geral.",
    "- `ARQUIVOS_IDENTICOS.csv`: copias de conteudo igual.",
    "- `AUDITORIA_GERAL.md`: verificacoes e pendencias.",
    "",
    "## Modos de visualizacao",
    "",
    "- VISUALIZACAO_AULAS.code-workspace",
    "- VISAO_GERAL.code-workspace",
    "",
    "Nenhum codigo anterior foi apagado ou movido.",
    "",
])

(saida / "INDICE_PROJETO.md").write_text(
    "\n".join(indice),
    encoding="utf-8",
)


print("\n===== 10. GERANDO RELATORIO FINAL =====")

relatorio = [
    "# Auditoria Geral - Databricks MLOps",
    "",
    "Data: " + datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    ),
    "",
    f"- Arquivos inventariados: {len(arquivos)}",
    f"- Grupos de copias identicas: {len(duplicados)}",
    f"- Backups/temporarios: {len(temporarios)}",
    f"- Arquivos grandes (10 MB ou mais): {len(grandes)}",
    "",
    "## Verificacoes",
    "",
    "| Verificacao | Resultado | Detalhe |",
    "|---|---|---|",
]

for item in verificacoes:
    relatorio.append(
        f"| {item['nome']} | {item['estado']} | "
        f"{item['detalhe'].replace('|', '/')} |"
    )

relatorio.extend([
    "",
    "## Pontos de atencao",
    "",
])

if problemas:
    relatorio.extend(f"- {p}" for p in problemas)
else:
    relatorio.append(
        "- Nenhum problema nas verificacoes realizadas."
    )

relatorio.extend([
    "",
    "## Backups e temporarios identificados",
    "",
])

if temporarios:
    relatorio.extend(
        f"- `{p}`" for p in temporarios[:35]
    )

    if len(temporarios) > 35:
        relatorio.append(
            f"- Mais {len(temporarios) - 35} arquivos "
            "(consulte INVENTARIO.csv)."
        )
else:
    relatorio.append("- Nenhum encontrado.")

relatorio.extend([
    "",
    "## Arquivos grandes",
    "",
])

if grandes:
    for item in grandes[:25]:
        tamanho = item["bytes"] / (1024 * 1024)

        relatorio.append(
            f"- `{item['caminho']}` - {tamanho:.1f} MB"
        )
else:
    relatorio.append("- Nenhum encontrado.")

relatorio.extend([
    "",
    "## Organizacao aplicada",
    "",
    "- Workspace focado nas aulas criado.",
    "- Workspace de visao geral criado.",
    "- Indice e inventario gerados.",
    "- Caches ocultos somente no Explorador.",
    "- Arquivos anteriores preservados.",
    "- Configuracoes globais do VS Code preservadas.",
    "- Nenhum deploy remoto realizado.",
    "",
    "## Limitacoes",
    "",
    "- Esta auditoria nao executa Spark nem MLflow.",
    "- Nao verifica Jobs remotos do Databricks.",
    "- Copias identicas podem ser intencionais.",
    "- Nenhum arquivo foi removido automaticamente.",
    "",
])

(saida / "AUDITORIA_GERAL.md").write_text(
    "\n".join(relatorio),
    encoding="utf-8",
)

print("\n===== AUDITORIA FINAL =====")
print("ARQUIVOS:", len(arquivos))
print("COPIAS IDENTICAS:", len(duplicados))
print("BACKUPS/TEMPORARIOS:", len(temporarios))
print("PONTOS DE ATENCAO:", len(problemas))
print("INDICE: CRIADO")
print("RELATORIO: CRIADO")
print("WORKSPACE ORGANIZADO: CRIADO")
print("ARQUIVOS ORIGINAIS: PRESERVADOS")
print("AUDITORIA E ORGANIZACAO: CONCLUIDAS")