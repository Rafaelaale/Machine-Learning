import csv
import json
import math
import random
import sqlite3
import sys

from datetime import datetime, timedelta, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parent
DADOS = BASE / "dados"
LOGS = BASE / "logs"

DADOS.mkdir(parents=True, exist_ok=True)
LOGS.mkdir(parents=True, exist_ok=True)

INICIO = sys.argv[1] if len(sys.argv) > 1 else "20260501"
FIM = sys.argv[2] if len(sys.argv) > 2 else "20260601"

dt_inicio = datetime.strptime(INICIO, "%Y%m%d")
dt_fim = datetime.strptime(FIM, "%Y%m%d")

dias = (dt_fim - dt_inicio).days

if not 1 <= dias <= 366:
    raise ValueError("Periodo invalido: 1 a 366 dias")

FEATURES = [
    "renda_mensal_k",
    "tempo_medio_clique_segundos"
]

TARGET = "comprou_eletronico"

COLUNAS = [
    "dia_prtc",
    "renda_mensal_k",
    "tempo_medio_clique_segundos",
    "media_interacoes_suporte",
    "media_cupons_ativos",
    "media_score_nps_cliente",
    "media_dias_inatividade",
    "total_gasto_acumulado_reais",
    "genero_cliente_m",
    "regiao_cliente_nordeste",
    "regiao_cliente_norte",
    "regiao_cliente_sudeste",
    "regiao_cliente_sul",
    TARGET
]


def sigmoid(valor):
    valor = max(-50.0, min(50.0, valor))
    return 1.0 / (1.0 + math.exp(-valor))


def gerar_registro(rng, producao=False, dia=""):
    regioes = [
        "nordeste", "norte", "sudeste", "sul", "outro"
    ]

    regiao = rng.choices(
        regioes,
        weights=[0.2, 0.1, 0.4, 0.2, 0.1],
        k=1
    )[0]

    if producao:
        renda = rng.uniform(0, 2000)
        clique = rng.uniform(10, 30)
        suporte = rng.uniform(30, 200)
        gasto = rng.uniform(1000, 20500)

        score = (
            gasto * 0.1
            + suporte * 0.05
            - 300
        )
    else:
        renda = rng.uniform(700, 25000)
        clique = rng.uniform(0, 150)
        suporte = rng.uniform(0, 150)
        gasto = rng.uniform(0, 7500)

        score = (
            renda * 0.1
            + gasto * 0.1
            - 1400
        )

    return {
        "dia_prtc": dia,
        "renda_mensal_k": renda,
        "tempo_medio_clique_segundos": clique,
        "media_interacoes_suporte": suporte,
        "media_cupons_ativos": rng.uniform(0, 15),
        "media_score_nps_cliente": rng.randrange(
            8 if producao else 10
        ),
        "media_dias_inatividade": rng.randrange(120),
        "total_gasto_acumulado_reais": gasto,
        "genero_cliente_m": int(rng.random() < 0.48),
        "regiao_cliente_nordeste": int(regiao == "nordeste"),
        "regiao_cliente_norte": int(regiao == "norte"),
        "regiao_cliente_sudeste": int(regiao == "sudeste"),
        "regiao_cliente_sul": int(regiao == "sul"),
        TARGET: int(rng.random() < sigmoid(score))
    }


def salvar_csv(caminho, registros):
    with caminho.open(
        "w", newline="", encoding="utf-8-sig"
    ) as arquivo:
        writer = csv.DictWriter(
            arquivo, fieldnames=COLUNAS
        )
        writer.writeheader()
        writer.writerows(registros)


def teste_ks(amostra_a, amostra_b):
    a = sorted(amostra_a)
    b = sorted(amostra_b)

    n = len(a)
    m = len(b)

    if min(n, m) < 2:
        raise ValueError("Amostras insuficientes para KS")

    i = j = 0
    estatistica = 0.0

    while i < n or j < m:
        if j == m or (i < n and a[i] <= b[j]):
            atual = a[i]
        else:
            atual = b[j]

        while i < n and a[i] <= atual:
            i += 1

        while j < m and b[j] <= atual:
            j += 1

        estatistica = max(
            estatistica,
            abs(i / n - j / m)
        )

    n_efetivo = n * m / (n + m)

    raiz = math.sqrt(n_efetivo)

    lam = (
        raiz + 0.12 + 0.11 / raiz
    ) * estatistica

    pvalue = 2 * sum(
        ((-1) ** (k - 1))
        * math.exp(-2 * k * k * lam * lam)
        for k in range(1, 101)
    )

    return estatistica, max(0.0, min(1.0, pvalue))


print("===== GERANDO TREINAMENTO =====")

rng_treino = random.Random(42)

treino = [
    gerar_registro(rng_treino)
    for _ in range(10000)
]

salvar_csv(
    DADOS / "treinamento_10000.csv",
    treino
)

print("TREINAMENTO:", len(treino))


print("===== GERANDO DADOS PRODUTIVOS =====")

rng_prod = random.Random(int(INICIO))

particoes = [
    (dt_inicio + timedelta(days=offset)).strftime("%Y%m%d")
    for offset in range(dias)
    for _ in range(100)
]

rng_prod.shuffle(particoes)

producao = [
    gerar_registro(rng_prod, True, dia)
    for dia in particoes
]

assert len(producao) == dias * 100
assert len(set(particoes)) == dias

salvar_csv(
    DADOS / f"producao_{INICIO}_{FIM}.csv",
    producao
)

print("PRODUCAO:", len(producao))
print("DIAS:", dias)


print("===== EXECUTANDO MONITORAMENTO =====")

logs = []

timestamp = datetime.now(
    timezone.utc
).isoformat(timespec="seconds")

for feature in FEATURES:
    treino_amostra = random.Random(42).sample(
        treino, max(2, len(treino) // 10)
    )

    prod_amostra = random.Random(43).sample(
        producao, max(2, len(producao) // 10)
    )

    estatistica, pvalue = teste_ks(
        [r[feature] for r in treino_amostra],
        [r[feature] for r in prod_amostra]
    )

    logs.append({
        "timestamp_execucao": timestamp,
        "periodo_inicio": INICIO,
        "periodo_fim": FIM,
        "nome_metrica": "Feature drift KS: p-value",
        "variavel": feature,
        "valor_calculado": pvalue,
        "threshold_alerta": 0.05,
        "drift_detectado": int(pvalue < 0.05),
        "estatistica_ks": estatistica
    })

media_treino = sum(
    r[TARGET] for r in treino
) / len(treino)

media_prod = sum(
    r[TARGET] for r in producao
) / len(producao)

if media_treino > 0:
    variacao = abs(
        media_prod - media_treino
    ) / media_treino
else:
    variacao = abs(media_prod - media_treino)

logs.append({
    "timestamp_execucao": timestamp,
    "periodo_inicio": INICIO,
    "periodo_fim": FIM,
    "nome_metrica": "Target drift: variacao relativa",
    "variavel": TARGET,
    "valor_calculado": variacao,
    "threshold_alerta": 0.15,
    "drift_detectado": int(variacao > 0.15),
    "estatistica_ks": None
})


print("===== GRAVANDO LOGS NO SQLITE =====")

banco = LOGS / "monitoramento_drift.sqlite"

with sqlite3.connect(banco) as conn:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS log_monitoramento_drift (
            periodo_inicio TEXT NOT NULL,
            periodo_fim TEXT NOT NULL,
            nome_metrica TEXT NOT NULL,
            variavel TEXT NOT NULL,
            timestamp_execucao TEXT NOT NULL,
            valor_calculado REAL NOT NULL,
            threshold_alerta REAL NOT NULL,
            drift_detectado INTEGER NOT NULL,
            estatistica_ks REAL,
            PRIMARY KEY (
                periodo_inicio,
                periodo_fim,
                nome_metrica,
                variavel
            )
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS historico_alertas (
            periodo_inicio TEXT NOT NULL,
            periodo_fim TEXT NOT NULL,
            data_alerta TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            PRIMARY KEY (periodo_inicio, periodo_fim)
        )
    """)

    campos = [
        "periodo_inicio", "periodo_fim",
        "nome_metrica", "variavel",
        "timestamp_execucao", "valor_calculado",
        "threshold_alerta", "drift_detectado",
        "estatistica_ks"
    ]

    for log in logs:
        conn.execute(
            """
            INSERT OR REPLACE INTO log_monitoramento_drift
            (
                periodo_inicio,
                periodo_fim,
                nome_metrica,
                variavel,
                timestamp_execucao,
                valor_calculado,
                threshold_alerta,
                drift_detectado,
                estatistica_ks
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            tuple(log[c] for c in campos)
        )

    total_alertas = conn.execute(
        """
        SELECT COUNT(*)
        FROM log_monitoramento_drift
        WHERE drift_detectado = 1
          AND periodo_inicio = ?
          AND periodo_fim = ?
        """,
        (INICIO, FIM)
    ).fetchone()[0]

    notificado = conn.execute(
        """
        SELECT COUNT(*)
        FROM historico_alertas
        WHERE periodo_inicio = ?
          AND periodo_fim = ?
        """,
        (INICIO, FIM)
    ).fetchone()[0] > 0

    if total_alertas > 0 and not notificado:
        conn.execute(
            """
            INSERT INTO historico_alertas
            VALUES (?, ?, ?, ?)
            """,
            (
                INICIO, FIM,
                timestamp, total_alertas
            )
        )


with (
    LOGS / "log_monitoramento_drift.csv"
).open("w", newline="", encoding="utf-8-sig") as arquivo:
    writer = csv.DictWriter(
        arquivo,
        fieldnames=list(logs[0].keys())
    )
    writer.writeheader()
    writer.writerows(logs)


status = "TRIGGERED" if total_alertas > 0 else "OK"

resultado = {
    "status": status,
    "periodo_inicio": INICIO,
    "periodo_fim_exclusivo": FIM,
    "registros_treinamento": len(treino),
    "registros_producao": len(producao),
    "numero_dias": dias,
    "metricas": logs,
    "quantidade_alertas": total_alertas,
    "notificacao_nova": bool(
        total_alertas > 0 and not notificado
    ),
    "entrega": "local - sem email ou Databricks",
    "metodo_ks": "KS com p-value assintotico aproximado"
}

(LOGS / "resultado_alerta.json").write_text(
    json.dumps(resultado, indent=2, ensure_ascii=False),
    encoding="utf-8"
)

mensagem = (
    f"AULA ALERTAS - {status}\n"
    f"Periodo: {INICIO} a {FIM} (fim exclusivo)\n"
    f"Treinamento: {len(treino)}\n"
    f"Producao: {len(producao)}\n"
    f"Particoes: {dias}\n"
    f"Drifts detectados: {total_alertas} de {len(logs)}\n"
    f"Notificacao nova: "
    f"{'SIM' if total_alertas and not notificado else 'NAO'}\n"
)

for log in logs:
    mensagem += (
        f"{log['variavel']}: "
        f"valor={log['valor_calculado']:.8g}; "
        f"alerta={bool(log['drift_detectado'])}\n"
    )

(LOGS / "ALERTA_DRIFT.txt").write_text(
    mensagem,
    encoding="utf-8"
)

print("\n===== RESULTADO DO ALERTA =====")
print(mensagem)

print("===== AUDITORIA =====")
print("Banco SQLite:", banco)
print("Dados e logs salvos no projeto")
print("Nenhum arquivo da Alura modificado")
print("Nenhum Job remoto executado")