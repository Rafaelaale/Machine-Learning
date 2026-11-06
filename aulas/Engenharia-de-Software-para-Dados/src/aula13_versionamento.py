"""Aula 13: preparacao segura para versionamento.

Este modulo nao executa comandos Git.
"""

import re
from pathlib import Path


PASTAS_RESTRITAS = {
    ".venv",
    "venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
}

ARQUIVOS_RESTRITOS = {
    ".env",
    ".env.local",
    ".coverage",
}

EXTENSOES_RESTRITAS = {
    ".pkl",
    ".pickle",
    ".joblib",
    ".key",
    ".pem",
}


def validar_nome_branch(nome: str) -> bool:
    """Aceita branches simples com tipo e descricao."""
    if not isinstance(nome, str):
        return False

    return bool(
        re.fullmatch(
            r"(feature|fix|docs|test)/"
            r"[a-z0-9]+(?:-[a-z0-9]+)*",
            nome,
        )
    )


def avaliar_arquivo(caminho: str) -> dict:
    """Classifica arquivos para revisao antes de publicar."""
    arquivo = Path(caminho)
    partes = {parte.lower() for parte in arquivo.parts}
    nome = arquivo.name.lower()

    if partes & PASTAS_RESTRITAS:
        return {
            "status": "nao_publicar",
            "motivo": "Ambiente ou cache local",
        }

    if (
        nome in ARQUIVOS_RESTRITOS
        or nome.startswith(".env.")
        or nome.startswith(".coverage")
        or arquivo.suffix.lower() in EXTENSOES_RESTRITAS
    ):
        return {
            "status": "nao_publicar",
            "motivo": "Segredo ou artefato binario",
        }

    if (
        "data" in partes
        or "dados" in partes
        or "material_alura" in partes
        or "resultados" in partes
        or "processed" in partes
    ):
        return {
            "status": "revisar",
            "motivo": "Dados, direitos de uso ou resultados",
        }

    if arquivo.suffix.lower() in {".py", ".md", ".txt"}:
        return {
            "status": "candidato",
            "motivo": "Codigo ou documentacao a revisar",
        }

    return {
        "status": "revisar",
        "motivo": "Formato nao classificado",
    }


def auditar_projeto(raiz: Path) -> dict:
    """Resume os arquivos existentes sem altera-los."""
    raiz = Path(raiz)

    if not raiz.is_dir():
        raise FileNotFoundError(raiz)

    contagem = {
        "candidato": 0,
        "revisar": 0,
        "nao_publicar": 0,
    }

    exemplos_revisao = []
    total = 0

    for arquivo in raiz.rglob("*"):
        if not arquivo.is_file():
            continue

        relativo = arquivo.relative_to(raiz)
        avaliacao = avaliar_arquivo(str(relativo))
        status = avaliacao["status"]

        total += 1
        contagem[status] += 1

        if status != "candidato" and len(exemplos_revisao) < 15:
            exemplos_revisao.append({
                "arquivo": str(relativo),
                "status": status,
                "motivo": avaliacao["motivo"],
            })

    return {
        "total_arquivos": total,
        "classificacao": contagem,
        "exemplos_que_exigem_atencao": exemplos_revisao,
        "publicacao_realizada": False,
        "nota": (
            "Triagem preliminar. Nao inspeciona conteudo "
            "nem comprova seguranca ou direitos de uso."
        ),
    }
