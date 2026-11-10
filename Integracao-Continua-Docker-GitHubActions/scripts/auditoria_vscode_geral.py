from pathlib import Path
from collections import Counter
from datetime import datetime
import ast
import json
import os
import re
import tokenize

ROOT = Path(r"F:\Projetos\Docker-GitHubActions-CI-CD")
REPO = ROOT / "docker-automation"
APP = REPO / "burguer-app"
AULAS = ROOT / "aulas"
RELATORIOS = ROOT / "relatorios" / "auditoria-vscode"

SERVICOS = [
    "auth-service",
    "user-service",
    "order-service",
    "product-service",
]

IGNORAR = {
    ".git", ".venv", "venv", "__pycache__",
    "node_modules", "site-packages", ".pytest_cache",
    ".mypy_cache", "dist", "build",
}

achados = []
estatisticas = Counter()


def registrar(nivel, categoria, mensagem):
    achados.append({
        "nivel": nivel,
        "categoria": categoria,
        "mensagem": mensagem,
    })
    estatisticas[nivel] += 1


def ler_texto(arquivo):
    return arquivo.read_text(encoding="utf-8-sig")


def conferir_arquivo(caminho, categoria):
    if caminho.is_file():
        estatisticas["arquivos_conferidos"] += 1
        return True

    registrar("ERRO", categoria, f"Arquivo ausente: {caminho.relative_to(ROOT)}")
    return False


def conferir_python():
    print("\n===== 1. AUDITORIA DE CODIGO PYTHON =====")

    total = 0
    problemas = 0

    for pasta, diretorios, arquivos in os.walk(ROOT):
        diretorios[:] = [
            nome for nome in diretorios
            if nome not in IGNORAR
        ]

        for nome in arquivos:
            if not nome.endswith(".py"):
                continue

            caminho = Path(pasta) / nome
            total += 1

            try:
                with tokenize.open(caminho) as arquivo:
                    codigo = arquivo.read()

                ast.parse(codigo, filename=str(caminho))

            except (SyntaxError, UnicodeError, OSError, ValueError) as erro:
                problemas += 1
                registrar(
                    "ERRO",
                    "Python",
                    f"{caminho.relative_to(ROOT)}: "
                    f"{type(erro).__name__}"
                )

    estatisticas["arquivos_python"] = total
    estatisticas["erros_python"] = problemas

    print(f"Arquivos Python analisados: {total}")
    print(f"Erros encontrados: {problemas}")


def conferir_microservicos():
    print("\n===== 2. AUDITORIA DOS MICROSSERVICOS =====")

    for servico in SERVICOS:
        pasta = APP / servico

        print(f"\nSERVICO: {servico}")

        if not pasta.is_dir():
            registrar("ERRO", servico, "Diretorio ausente")
            continue

        for nome in ("Dockerfile", "requirements.txt", "app.py"):
            arquivo = pasta / nome

            if conferir_arquivo(arquivo, servico):
                print(f"  OK: {nome}")

        dockerignore = pasta / ".dockerignore"

        if conferir_arquivo(dockerignore, servico):
            conteudo = ler_texto(dockerignore)

            if not re.search(r"(?m)^\s*(?:\*\*/)?\.env(?:\*|$)", conteudo):
                registrar(
                    "ALERTA",
                    servico,
                    ".dockerignore pode nao excluir arquivos .env"
                )

        dockerfile = pasta / "Dockerfile"

        if dockerfile.is_file():
            conteudo = ler_texto(dockerfile)

            bases = re.findall(
                r"(?mi)^\s*FROM\s+([^\s]+)",
                conteudo
            )

            if not bases:
                registrar("ERRO", servico, "Dockerfile sem FROM")
            else:
                estatisticas["dockerfiles"] += 1

            if not re.search(r"(?mi)^\s*USER\s+", conteudo):
                registrar(
                    "AVISO",
                    servico,
                    "Revisar se o container executa com usuario nao-root"
                )

    print("\nInventario dos quatro servicos concluido.")


def conferir_seguranca():
    print("\n===== 3. AUDITORIA DE SEGURANCA =====")

    auth = APP / "auth-service"
    app = auth / "app.py"
    env = auth / ".env"

    if env.exists():
        registrar(
            "ALERTA",
            "Credenciais",
            "auth-service/.env existe; houve alerta anterior "
            "de rastreamento. Revisar antes de publicar."
        )

    if not app.is_file():
        return

    try:
        with tokenize.open(app) as arquivo:
            codigo = arquivo.read()

        arvore = ast.parse(codigo)

        for node in ast.walk(arvore):
            if not isinstance(node, ast.Call):
                continue

            if isinstance(node.func, ast.Name) and node.func.id == "print":
                argumentos = " ".join(
                    ast.dump(arg).lower() for arg in node.args
                )

                if "secret_key" in argumentos:
                    registrar(
                        "ALERTA",
                        "Credenciais",
                        "app.py pode imprimir SECRET_KEY no terminal"
                    )

            for keyword in node.keywords:
                if keyword.arg != "debug":
                    continue

                if (
                    isinstance(keyword.value, ast.Constant)
                    and keyword.value.value is True
                ):
                    registrar(
                        "ALERTA",
                        "Flask",
                        "debug=True identificado; desabilitar em producao"
                    )

    except (SyntaxError, UnicodeError, OSError):
        registrar(
            "ERRO",
            "Seguranca",
            "Nao foi possivel analisar a AST do auth-service"
        )

    requirements = auth / "requirements.txt"

    if requirements.is_file():
        texto = ler_texto(requirements)

        if re.search(
            r"(?mi)^\s*prometheus[-_]client\s*==",
            texto
        ):
            print("Dependencia Prometheus declarada.")
        else:
            registrar(
                "ERRO",
                "Dependencias",
                "prometheus_client nao esta fixado no requirements.txt"
            )

    print("Verificacao estatica de seguranca concluida.")
    print("Valores de credenciais nao foram exibidos.")


def conferir_observabilidade():
    print("\n===== 4. AUDITORIA PROMETHEUS E GRAFANA =====")

    arquivos = {
        "Prometheus": AULAS / "observabilidade/prometheus.yml",
        "Compose Prometheus": AULAS / "prometheus-compose-aula.override.yml",
        "Compose Grafana": AULAS / "grafana-compose-aula.override.yml",
        "Datasource": AULAS / "observabilidade/grafana/provisioning/datasources/prometheus.yml",
        "Provider": AULAS / "observabilidade/grafana/provisioning/dashboards/default.yml",
        "Dashboard": AULAS / "observabilidade/grafana/dashboards/microservicos.json",
    }

    for nome, caminho in arquivos.items():
        if conferir_arquivo(caminho, "Observabilidade"):
            print(f"OK: {nome}")

    dashboard = arquivos["Dashboard"]

    if dashboard.is_file():
        try:
            dados = json.loads(ler_texto(dashboard))
            paineis = dados.get("panels", [])

            estatisticas["paineis_grafana"] = len(paineis)

            consultas = []

            for painel in paineis:
                for target in painel.get("targets", []):
                    consultas.append(target.get("expr", ""))

            esperadas = [
                "process_cpu_seconds_total",
                "process_open_fds",
                "auth_service_metrics_scrapes_total",
            ]

            for metrica in esperadas:
                if not any(metrica in consulta for consulta in consultas):
                    registrar(
                        "ERRO",
                        "Grafana",
                        f"Metrica ausente: {metrica}"
                    )

            print(f"Paineis encontrados: {len(paineis)}")

        except (ValueError, TypeError) as erro:
            registrar(
                "ERRO",
                "Grafana",
                f"JSON do dashboard invalido: {type(erro).__name__}"
            )

    datasource = arquivos["Datasource"]

    if datasource.is_file():
        texto = ler_texto(datasource)

        if "http://prometheus:9090" not in texto:
            registrar(
                "ERRO",
                "Grafana",
                "URL do Prometheus nao identificada"
            )

    prometheus = arquivos["Prometheus"]

    if prometheus.is_file():
        texto = ler_texto(prometheus)

        if "auth-service:5000" not in texto:
            registrar(
                "ERRO",
                "Prometheus",
                "Target do Auth Service nao encontrado"
            )

    registrar(
        "PENDENTE",
        "Observabilidade",
        "A conexao real Grafana-Prometheus ainda nao foi testada"
    )


def conferir_workflows():
    print("\n===== 5. AUDITORIA DE WORKFLOWS =====")

    rascunhos = sorted(AULAS.rglob("*rascunho*.yml"))

    for arquivo in rascunhos:
        texto = ler_texto(arquivo)

        if 'if: ${{ false }}' not in texto:
            registrar(
                "ALERTA",
                "Workflow",
                f"Verificar desativacao: {arquivo.relative_to(ROOT)}"
            )

    estatisticas["rascunhos"] = len(rascunhos)

    print(f"Rascunhos encontrados: {len(rascunhos)}")

    ativos = REPO / ".github" / "workflows"

    if ativos.is_dir():
        quantidade = len(list(ativos.glob("*.yml")))
        quantidade += len(list(ativos.glob("*.yaml")))

        estatisticas["workflows_ativos"] = quantidade

        print(f"Workflows na pasta ativa: {quantidade}")

        if quantidade:
            registrar(
                "AVISO",
                "Workflows",
                "Existem workflows em .github/workflows. "
                "Revisar gatilhos antes da publicacao final."
            )

    print("Nenhum workflow foi executado.")


def conferir_trivy():
    print("\n===== 6. AUDITORIA DOS RESULTADOS TRIVY =====")

    arquivo = ROOT / "relatorios/trivy/aula-218716-dependencias.json"

    if not conferir_arquivo(arquivo, "Trivy"):
        return

    try:
        dados = json.loads(ler_texto(arquivo))
    except (ValueError, TypeError):
        registrar("ERRO", "Trivy", "Relatorio JSON invalido")
        return

    severidades = Counter()
    pacotes = Counter()
    cves = set()

    for resultado in dados.get("Results", []):
        for vuln in resultado.get("Vulnerabilities") or []:
            severidade = vuln.get("Severity", "")

            if severidade not in ("HIGH", "CRITICAL"):
                continue

            severidades[severidade] += 1

            pacotes[vuln.get("PkgName") or "desconhecido"] += 1

            if vuln.get("VulnerabilityID"):
                cves.add(vuln["VulnerabilityID"])

    estatisticas["trivy_high"] = severidades["HIGH"]
    estatisticas["trivy_critical"] = severidades["CRITICAL"]
    estatisticas["cves_unicas"] = len(cves)

    print(f"HIGH: {severidades['HIGH']}")
    print(f"CRITICAL: {severidades['CRITICAL']}")
    print(f"Identificadores de CVE distintos: {len(cves)}")

    print("\nPacotes com mais ocorrencias:")

    for pacote, quantidade in pacotes.most_common(8):
        print(f"  {pacote}: {quantidade}")

    if severidades["CRITICAL"]:
        registrar(
            "ALERTA",
            "Trivy",
            f"{severidades['CRITICAL']} ocorrencias CRITICAL "
            "precisam de avaliacao"
        )

    if severidades["HIGH"]:
        registrar(
            "ALERTA",
            "Trivy",
            f"{severidades['HIGH']} ocorrencias HIGH "
            "precisam de avaliacao"
        )

    registrar(
        "PENDENTE",
        "Trivy",
        "Scan das imagens Docker ainda nao realizado"
    )


def salvar_relatorios():
    print("\n===== 7. GERANDO RELATORIOS =====")

    RELATORIOS.mkdir(parents=True, exist_ok=True)

    momento = datetime.now()
    identificador = momento.strftime("%Y%m%d-%H%M%S")

    txt = RELATORIOS / f"auditoria-{identificador}.txt"
    arquivo_json = RELATORIOS / f"auditoria-{identificador}.json"

    linhas = [
        "AUDITORIA GERAL DO PROJETO VS CODE",
        f"Data: {momento.strftime('%d/%m/%Y %H:%M:%S')}",
        f"Projeto: {ROOT}",
        "",
        "ESTATISTICAS",
    ]

    for chave, valor in sorted(estatisticas.items()):
        linhas.append(f"{chave}: {valor}")

    linhas.extend(["", "ACHADOS"])

    for item in achados:
        linhas.append(
            f"[{item['nivel']}] "
            f"{item['categoria']}: {item['mensagem']}"
        )

    linhas.extend([
        "",
        "LIMITACOES",
        "Auditoria estatica: nao executa os microservicos.",
        "Sintaxe YAML e funcionamento remoto nao comprovados.",
        "Nao executa testes pytest nem valida conexoes reais.",
        "Nao executa Git, Docker ou comandos de deploy.",
        "Nao le valores dos arquivos .env.",
        "Nao modifica os arquivos existentes.",
    ])

    txt.write_text("\n".join(linhas) + "\n", encoding="utf-8")

    estrutura = {
        "data": momento.isoformat(timespec="seconds"),
        "projeto": str(ROOT),
        "estatisticas": dict(estatisticas),
        "achados": achados,
        "auditoria_estatica": True,
    }

    arquivo_json.write_text(
        json.dumps(estrutura, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    print(f"RELATORIO TXT: {txt}")
    print(f"RELATORIO JSON: {arquivo_json}")

    return txt, arquivo_json


def main():
    print("========================================")
    print(" AUDITORIA PYTHON - VS CODE")
    print("========================================")

    if not REPO.is_dir():
        raise RuntimeError("Repositorio Docker Automation ausente")

    conferir_python()
    conferir_microservicos()
    conferir_seguranca()
    conferir_observabilidade()
    conferir_workflows()
    conferir_trivy()

    txt, arquivo_json = salvar_relatorios()

    print("\n===== RESULTADO FINAL =====")
    print(f"PYTHON ANALISADOS: {estatisticas['arquivos_python']}")
    print(f"ERROS DE SINTAXE: {estatisticas['erros_python']}")
    print(f"DOCKERFILES: {estatisticas['dockerfiles']}/4")
    print(f"PAINEIS GRAFANA: {estatisticas['paineis_grafana']}")
    print(f"ALERTAS: {estatisticas['ALERTA']}")
    print(f"ERROS: {estatisticas['ERRO']}")
    print(f"PENDENCIAS: {estatisticas['PENDENTE']}")
    print(f"RELATORIO: {txt}")
    print("AUDITORIA ESTATICA CONCLUIDA.")
    print("NENHUM CODIGO PUBLICADO.")
    print("NENHUM CONTAINER ALTERADO.")


if __name__ == "__main__":
    main()
