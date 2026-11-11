import ast
import json
import shutil
from datetime import datetime
from pathlib import Path

root = Path(r"F:\Projetos\Databricks-Engenharia-de-Machine-Learning-e-MLOps")
fontes = [
    root / "material-alura" / "aula_5",
    root / "material-alura" / "6123-alura-ml-databricks" / "aula_5"
]
destino = root / "aulas" / "aula_05_02_drift_aprimorado"

nomes = [
    "aula_5_2_gerando_dados",
    "aula_5_2_job_dados_prod",
    "aula_5_2_job_monitoramento_drift"
]

def original(nome):
    for pasta in fontes:
        arquivo = pasta / (nome + ".ipynb")
        if arquivo.is_file():
            nb = json.loads(arquivo.read_text(encoding="utf-8-sig"))
            codigo = "\n\n".join(
                "".join(c["source"])
                for c in nb["cells"]
                if c["cell_type"] == "code"
            )
            ast.parse(codigo)
            return codigo
    raise FileNotFoundError(nome)

def patch(codigo, antigo, novo):
    if codigo.count(antigo) != 1:
        raise ValueError(
            "Codigo oficial diferente do esperado. "
            "Nenhum notebook sera substituido. Trecho: "
            + antigo[:80]
        )
    return codigo.replace(antigo, novo, 1)

header = """
import re
from datetime import datetime

dbutils.widgets.text("gravar", "false")
dbutils.widgets.text("catalogo", "workspace")
dbutils.widgets.text("esquema", "default")

gravar = dbutils.widgets.get("gravar").strip().lower() == "true"
cat = dbutils.widgets.get("catalogo").strip()
esq = dbutils.widgets.get("esquema").strip()

for identificador in [cat, esq]:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z_0-9]*", identificador):
        raise ValueError("Nome de catalogo ou esquema invalido")
"""

datas = """
dbutils.widgets.text("data_inicio", "20260101")
dbutils.widgets.text("data_fim", "20260110")
"""

# =========================================
# 1. DADOS DE TREINAMENTO
# =========================================

treino = header + "\n" + original(nomes[0])

treino = patch(
    treino,
    "    # Target Treino",
    """    pdf_treino[
        ["media_score_nps_cliente", "media_dias_inatividade"]
    ] = pdf_treino[
        ["media_score_nps_cliente", "media_dias_inatividade"]
    ].astype(float)

    # Target Treino"""
)

treino = patch(
    treino,
    "np.exp(-(pdf_treino['renda_mensal_k']*0.1 + pdf_treino['total_gasto_acumulado_reais']*0.1 - 1400))",
    "np.exp(-np.clip(pdf_treino['renda_mensal_k']*0.1 + pdf_treino['total_gasto_acumulado_reais']*0.1 - 1400, -50, 50))"
)

treino = patch(
    treino,
    'nome_tabela_treino = "workspace.default.base_treinamento_modelo"',
    'nome_tabela_treino = f"{cat}.{esq}.base_treinamento_modelo_aprimorado"'
)

treino = patch(
    treino,
    '''df_treino.write.format("delta").mode("overwrite").saveAsTable(nome_tabela_treino)

print(f"Tabela de treino gravada com sucesso em: {nome_tabela_treino}")''',
    '''assert df_treino.count() == 10000

print("TREINAMENTO: 10000 registros")
df_treino.groupBy("comprou_eletronico").count().show()

if gravar:
    df_treino.write.format("delta").mode("overwrite").saveAsTable(
        nome_tabela_treino
    )
    print("GRAVADO:", nome_tabela_treino)
else:
    print("PREVIA: treinamento nao gravado")'''
)

# =========================================
# 2. DADOS PRODUTIVOS
# =========================================

prod = header + datas + "\n" + original(nomes[1])

prod = patch(
    prod,
    "    n_total = n_por_dia * dias_delta",
    """    if not 1 <= dias_delta <= 366:
        raise ValueError("Intervalo invalido: 1 a 366 dias")
    n_total = n_por_dia * dias_delta"""
)

prod = patch(
    prod,
    """    regioes = np.random.choice(['nordeste', 'norte', 'sudeste', 'sul', 'outro'], n_total, p=[0.2, 0.1, 0.4, 0.2, 0.1])
    
    np.random.seed(int(dt_inicio_str))
    random_offsets = np.random.randint(0, dias_delta, n_total)""",
    """    np.random.seed(int(dt_inicio_str))
    regioes = np.random.choice(
        ['nordeste', 'norte', 'sudeste', 'sul', 'outro'],
        n_total,
        p=[0.2, 0.1, 0.4, 0.2, 0.1]
    )

    random_offsets = np.repeat(np.arange(dias_delta), n_por_dia)
    np.random.shuffle(random_offsets)"""
)

prod = patch(
    prod,
    "    # Target Prod",
    """    pdf_prod[
        ["media_score_nps_cliente", "media_dias_inatividade"]
    ] = pdf_prod[
        ["media_score_nps_cliente", "media_dias_inatividade"]
    ].astype(float)

    # Target Prod"""
)

prod = patch(
    prod,
    "np.exp(-(pdf_prod['total_gasto_acumulado_reais']*0.1 + pdf_prod['media_interacoes_suporte']*0.05 - 300))",
    "np.exp(-np.clip(pdf_prod['total_gasto_acumulado_reais']*0.1 + pdf_prod['media_interacoes_suporte']*0.05 - 300, -50, 50))"
)

prod = patch(
    prod,
    'nome_tabela_prod = "workspace.default.base_tabela_prod"',
    'nome_tabela_prod = f"{cat}.{esq}.base_tabela_prod_aprimorada"'
)

prod = patch(
    prod,
    '''df_prod.write \\
    .format("delta") \\
    .partitionBy("dia_prtc") \\
    .mode("append") \\
    .saveAsTable(nome_tabela_prod)

print(f"Carga finalizada. {df_prod.count()} registros salvos em {nome_tabela_prod}.")''',
    '''qtd = df_prod.count()

dias = (
    datetime.strptime(p_fim, "%Y%m%d")
    - datetime.strptime(p_inicio, "%Y%m%d")
).days

assert qtd == dias * 100

print("PRODUCAO:", qtd, "registros")

df_prod.groupBy("dia_prtc").count().orderBy(
    "dia_prtc"
).show(366)

if gravar:
    if spark.catalog.tableExists(nome_tabela_prod):
        df_prod.write.format("delta").mode("overwrite").option(
            "replaceWhere",
            f"dia_prtc >= '{p_inicio}' AND dia_prtc < '{p_fim}'"
        ).saveAsTable(nome_tabela_prod)
    else:
        df_prod.write.format("delta").mode("overwrite").partitionBy(
            "dia_prtc"
        ).saveAsTable(nome_tabela_prod)

    print("GRAVADO:", nome_tabela_prod)
else:
    print("PREVIA: producao nao gravada")'''
)

# =========================================
# 3. MONITORAMENTO DE DRIFT
# =========================================

monitor = (
    header
    + datas
    + '''
dbutils.widgets.text(
    "features",
    "renda_mensal_k,tempo_medio_clique_segundos"
)
dbutils.widgets.text("target", "comprou_eletronico")
'''
    + original(nomes[2])
)

monitor = patch(
    monitor,
    '''nome_tabela_treino = "workspace.default.base_treinamento_modelo"
nome_tabela_prod = "workspace.default.base_tabela_prod"
nome_tabela_auditoria = "workspace.default.log_monitoramento_drift"''',
    '''nome_tabela_treino = f"{cat}.{esq}.base_treinamento_modelo_aprimorado"
nome_tabela_prod = f"{cat}.{esq}.base_tabela_prod_aprimorada"
nome_tabela_auditoria = f"{cat}.{esq}.log_monitoramento_drift_aprimorado"'''
)

monitor = patch(
    monitor,
    'F.col("dia_prtc").between(p_inicio, p_fim)',
    '(F.col("dia_prtc") >= p_inicio) & (F.col("dia_prtc") < p_fim)'
)

monitor = monitor[:monitor.index("qtd_prod = df_prod.count()")] + '''
if datetime.strptime(p_inicio, "%Y%m%d") >= datetime.strptime(
    p_fim, "%Y%m%d"
):
    raise ValueError("Periodo invalido")

if not lista_features:
    raise ValueError("Informe as features")

for coluna in lista_features + [p_target]:
    if coluna not in df_treino.columns or coluna not in df_prod.columns:
        raise ValueError("Coluna nao encontrada: " + coluna)

if df_prod.limit(1).count() == 0:
    raise ValueError("Sem dados produtivos no periodo")

logs_execucao = []

def registrar(nome, coluna, valor, limite):
    if "p-value" in nome.lower():
        alerta = float(valor) < limite
    else:
        alerta = float(valor) > limite

    logs_execucao.append((
        datetime.now(),
        p_inicio,
        p_fim,
        nome,
        coluna,
        float(valor),
        float(limite),
        bool(alerta)
    ))

def amostrar(df, coluna):
    base = df.select(coluna).where(F.col(coluna).isNotNull())

    serie = base.sample(
        fraction=0.1, seed=42
    ).limit(5000).toPandas()[coluna]

    if len(serie) < 2:
        serie = base.limit(5000).toPandas()[coluna]

    return serie.to_numpy(dtype=float)

for feature in lista_features:
    arr_treino = amostrar(df_treino, feature)
    arr_prod = amostrar(df_prod, feature)

    if min(len(arr_treino), len(arr_prod)) < 2:
        raise ValueError("Amostra insuficiente: " + feature)

    estatistica, pvalue = ks_2samp(
        arr_treino, arr_prod
    )

    print(
        f"KS {feature}: "
        f"estatistica={estatistica:.4f}, "
        f"p-value={pvalue:.6g}"
    )

    registrar(
        "Feature drift KS: p-value",
        feature,
        pvalue,
        0.05
    )

media_t = df_treino.select(F.avg(p_target)).first()[0]
media_p = df_prod.select(F.avg(p_target)).first()[0]

if media_t is None or media_p is None:
    raise ValueError("Target sem dados validos")

if media_t > 0:
    variacao = abs(media_p - media_t) / media_t
    nome = "Target drift: variacao relativa"
else:
    variacao = abs(media_p - media_t)
    nome = "Target drift: diferenca absoluta"

print(
    f"Target: treino={media_t:.4f}, "
    f"producao={media_p:.4f}, "
    f"variacao={variacao:.4f}"
)

registrar(nome, p_target, variacao, 0.15)

schema = StructType([
    StructField("timestamp_execucao", TimestampType(), False),
    StructField("periodo_inicio", StringType(), False),
    StructField("periodo_fim", StringType(), False),
    StructField("nome_metrica", StringType(), False),
    StructField("variavel", StringType(), False),
    StructField("valor_calculado", DoubleType(), False),
    StructField("threshold_alerta", DoubleType(), False),
    StructField("drift_detectado", BooleanType(), False)
])

df_logs = spark.createDataFrame(
    logs_execucao, schema=schema
)

df_logs.show(truncate=False)

print("TOTAL DE METRICAS:", len(logs_execucao))

if gravar:
    df_logs.write.format("delta").mode("append").saveAsTable(
        nome_tabela_auditoria
    )
    print("LOGS GRAVADOS:", nome_tabela_auditoria)
else:
    print("PREVIA: monitoramento nao gravado")
'''

# =========================================
# 4. VALIDAR ANTES DE GRAVAR
# =========================================

codigos = [treino, prod, monitor]
preparados = []

for nome, codigo in zip(nomes, codigos):
    ast.parse(codigo, filename=nome)

    notebook = {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# Aula 5.2 - Alura - versao aprimorada\\n"
                ]
            },
            {
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "outputs": [],
                "source": codigo.splitlines(keepends=True)
            }
        ],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {"name": "python"}
        },
        "nbformat": 4,
        "nbformat_minor": 5
    }

    conteudo = json.dumps(
        notebook,
        ensure_ascii=False,
        indent=2
    )

    json.loads(conteudo)
    preparados.append((nome + "_aprimorado.ipynb", conteudo))

# =========================================
# 5. BACKUP E GRAVACAO SEGURA
# =========================================

destino.mkdir(parents=True, exist_ok=True)

backup = destino / (
    "backup_antes_aula_52_"
    + datetime.now().strftime("%Y%m%d_%H%M%S")
)

relatorio = []

for nome, conteudo in preparados:
    arquivo = destino / nome

    if arquivo.exists():
        anterior = arquivo.read_text(encoding="utf-8-sig")

        if anterior == conteudo:
            print("JA VALIDADO:", nome)
            relatorio.append("SEM ALTERACAO: " + nome)
            continue

        backup.mkdir(exist_ok=True)
        shutil.copy2(arquivo, backup / nome)

    temporario = destino / (nome + ".tmp")
    temporario.write_text(conteudo, encoding="utf-8")

    json.loads(temporario.read_text(encoding="utf-8"))
    temporario.replace(arquivo)

    print("VALIDADO E ATUALIZADO:", nome)
    relatorio.append("VALIDADO: " + nome)

relatorio.extend([
    "SINTAXE PYTHON: OK",
    "ESTRUTURA NOTEBOOK: OK",
    "EXECUCAO SPARK: PENDENTE NO DATABRICKS"
])

(destino / "AUDITORIA_05_02.txt").write_text(
    "\n".join(relatorio) + "\n",
    encoding="utf-8"
)

print("\n===== AULA 5.2 PREPARADA =====")
print("Tres notebooks validados.")
print("Arquivos anteriores preservados em backup.")
print("Projeto:", root)