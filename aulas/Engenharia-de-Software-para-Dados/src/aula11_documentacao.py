"""Verificacoes reutilizaveis da documentacao do churn."""

from pathlib import Path
import re


DOCUMENTOS = {
    "problema": "doc/PROBLEMA_NEGOCIO.md",
    "dados": "doc/DICIONARIO_DADOS.md",
    "regras": "doc/REGRAS_NEGOCIO.md",
    "arquitetura": "doc/ARQUITETURA.md",
    "responsabilidades": "doc/RESPONSABILIDADES.md",
    "licenciamento": "doc/LICENCIAMENTO.md",
    "executivo": "doc/reports/RESUMO_EXECUTIVO.md",
}


def verificar_documentos(raiz: Path) -> dict:
    """Identifica documentos ausentes ou vazios."""
    raiz = Path(raiz)
    ausentes = []
    vazios = []

    for relativo in ["README.md", *DOCUMENTOS.values()]:
        arquivo = raiz / relativo

        if not arquivo.is_file():
            ausentes.append(relativo)
        elif not arquivo.read_text(
            encoding="utf-8"
        ).strip():
            vazios.append(relativo)

    return {
        "total_esperado": len(DOCUMENTOS) + 1,
        "ausentes": ausentes,
        "vazios": vazios,
        "aprovado": not ausentes and not vazios,
    }


def verificar_links_readme(raiz: Path) -> dict:
    """Verifica se links locais Markdown apontam para arquivos."""
    raiz = Path(raiz)
    readme = raiz / "README.md"

    if not readme.is_file():
        raise FileNotFoundError(readme)

    conteudo = readme.read_text(encoding="utf-8")

    links = re.findall(
        r"\[[^\]]+\]\(([^)]+)\)",
        conteudo,
    )

    locais = [
        link.split("#")[0]
        for link in links
        if not link.startswith(("http://", "https://", "#"))
    ]

    quebrados = [
        link
        for link in locais
        if not (raiz / link).exists()
    ]

    return {
        "links_locais": len(locais),
        "links_quebrados": quebrados,
        "aprovado": not quebrados,
    }


def verificar_termos_essenciais(raiz: Path) -> dict:
    """Verifica informacoes essenciais no resumo executivo."""
    arquivo = (
        Path(raiz)
        / "doc"
        / "reports"
        / "RESUMO_EXECUTIVO.md"
    )

    conteudo = arquivo.read_text(encoding="utf-8").lower()

    termos = (
        "problema",
        "10.000",
        "recall",
        "0%",
        "producao",
    )

    ausentes = [
        termo
        for termo in termos
        if termo not in conteudo
    ]

    return {
        "termos_ausentes": ausentes,
        "aprovado": not ausentes,
    }
