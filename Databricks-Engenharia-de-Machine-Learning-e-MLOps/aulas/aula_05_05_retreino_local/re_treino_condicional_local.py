import csv
import hashlib
import json
import math
import random
import sqlite3
import sys

from pathlib import Path

FEATURES = [
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
    "regiao_cliente_sul"
]

TARGET = "comprou_eletronico"


def salvar_json(caminho, dados):
    temp = caminho.with_name(caminho.name + ".tmp")
    temp.write_text(
        json.dumps(dados, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )
    temp.replace(caminho)


def auc_binaria(verdadeiro, escores):
    positivos = sum(verdadeiro)
    negativos = len(verdadeiro) - positivos

    if not positivos or not negativos:
        raise ValueError("AUC indisponivel: validacao com classe unica")

    ordem = sorted(
        zip(escores, verdadeiro),
        key=lambda item: item[0]
    )

    soma = 0.0
    indice = 0

    while indice < len(ordem):
        fim = indice + 1

        while (
            fim < len(ordem)
            and ordem[fim][0] == ordem[indice][0]
        ):
            fim += 1

        posto = ((indice + 1) + fim) / 2.0

        soma += posto * sum(
            classe for _, classe in ordem[indice:fim]
        )

        indice = fim

    return (
        soma - positivos * (positivos + 1) / 2
    ) / (positivos * negativos)


def dividir_estratificado(x, y):
    grupos = {0: [], 1: []}

    for indice, classe in enumerate(y):
        grupos[classe].append(indice)

    if min(len(grupos[0]), len(grupos[1])) < 4:
        raise ValueError("Dados insuficientes das duas classes")

    sorteio = random.Random(42)
    treino = []
    validacao = []

    for indices in grupos.values():
        sorteio.shuffle(indices)

        quantidade = max(2, round(len(indices) * 0.20))

        validacao.extend(indices[:quantidade])
        treino.extend(indices[quantidade:])

    sorteio.shuffle(treino)
    sorteio.shuffle(validacao)

    return (
        [x[i] for i in treino],
        [y[i] for i in treino],
        [x[i] for i in validacao],
        [y[i] for i in validacao]
    )


def regressao_logistica(x_treino, y_treino, x_validacao):
    quantidade_features = len(FEATURES)
    n = len(x_treino)

    medias = [
        sum(linha[j] for linha in x_treino) / n
        for j in range(quantidade_features)
    ]

    desvios = []

    for j in range(quantidade_features):
        variancia = sum(
            (linha[j] - medias[j]) ** 2
            for linha in x_treino
        ) / n

        desvios.append(max(math.sqrt(variancia), 1e-9))

    def normalizar(matriz):
        return [
            [
                (linha[j] - medias[j]) / desvios[j]
                for j in range(quantidade_features)
            ]
            for linha in matriz
        ]

    x_treino = normalizar(x_treino)
    x_validacao = normalizar(x_validacao)

    pesos = [0.0] * quantidade_features
    vies = 0.0

    for _ in range(280):
        gradientes = [0.0] * quantidade_features
        gradiente_vies = 0.0

        for linha, classe in zip(x_treino, y_treino):
            z = vies + sum(
                p * valor for p, valor in zip(pesos, linha)
            )

            z = max(-35, min(35, z))
            probabilidade = 1 / (1 + math.exp(-z))
            erro = probabilidade - classe

            gradiente_vies += erro

            for j in range(quantidade_features):
                gradientes[j] += erro * linha[j]

        taxa = 0.35

        for j in range(quantidade_features):
            pesos[j] -= taxa * (
                gradientes[j] / n + 0.001 * pesos[j]
            )

        vies -= taxa * gradiente_vies / n

    probabilidades = []

    for linha in x_validacao:
        z = vies + sum(
            p * valor for p, valor in zip(pesos, linha)
        )

        z = max(-35, min(35, z))
        probabilidades.append(1 / (1 + math.exp(-z)))

    modelo = {
        "algoritmo": "Regressao logistica - Python puro",
        "features": FEATURES,
        "medias": medias,
        "desvios": desvios,
        "pesos": pesos,
        "intercepto": vies
    }

    return probabilidades, modelo, "modelo_logistico.json"


def executar(origem, destino, inicio, fim):
    if not (
        len(inicio) == len(fim) == 8
        and inicio.isdigit()
        and fim.isdigit()
        and inicio < fim
    ):
        raise ValueError("Datas invalidas: YYYYMMDD")

    banco = origem / "logs" / "monitoramento_drift.sqlite"
    csv_prod = origem / "dados" / f"producao_{inicio}_{fim}.csv"

    if not banco.is_file() or not csv_prod.is_file():
        raise FileNotFoundError(
            "Dados da aula anterior nao encontrados"
        )

    print("\n===== 1. VERIFICAR DRIFT =====")

    with sqlite3.connect(banco) as conexao:
        total_drift = conexao.execute(
            """
            SELECT COUNT(*)
            FROM log_monitoramento_drift
            WHERE periodo_inicio = ?
              AND periodo_fim = ?
              AND drift_detectado = 1
            """,
            (inicio, fim)
        ).fetchone()[0]

    print("Drifts detectados:", total_drift)

    destino.mkdir(parents=True, exist_ok=True)

    resultado = {
        "data_inicio": inicio,
        "data_fim_exclusivo": fim,
        "total_drift": total_drift,
        "execucao_remota": False
    }

    print("\n===== 2. CONDICAO =====")

    if total_drift == 0:
        resultado.update(
            status="SEM_DRIFT",
            retreino_executado=False,
            motivo="Condicao falsa: total_drift = 0"
        )
        salvar_json(
            destino / "RESULTADO_RETREINO.json", resultado
        )
        print("Modelo estavel. Retreino nao acionado.")
        return resultado

    print("DRIFT DETECTADO. Acionando retreino.")

    hash_dados = hashlib.sha256(
        csv_prod.read_bytes()
    ).hexdigest()

    chave = f"{inicio}_{fim}_{hash_dados[:16]}"

    registro_arquivo = destino / "REGISTRO_MODELOS.json"

    if registro_arquivo.exists():
        registro = json.loads(
            registro_arquivo.read_text(encoding="utf-8")
        )
    else:
        registro = {
            "champion": None,
            "modelos": [],
            "execucoes": {}
        }

    if chave in registro["execucoes"]:
        resultado.update(
            status="JA_EXECUTADO",
            retreino_executado=False,
            modelo_existente=registro["execucoes"][chave]
        )
        salvar_json(
            destino / "RESULTADO_RETREINO.json", resultado
        )
        print("Retreino anterior identificado. Sem duplicacao.")
        return resultado

    print("\n===== 3. LENDO DADOS PRODUTIVOS =====")

    x = []
    y = []

    with csv_prod.open(
        newline="", encoding="utf-8-sig"
    ) as arquivo:
        leitor = csv.DictReader(arquivo)

        obrigatorias = FEATURES + [TARGET, "dia_prtc"]

        if (
            not leitor.fieldnames
            or any(c not in leitor.fieldnames for c in obrigatorias)
        ):
            raise ValueError("CSV sem as colunas necessarias")

        for linha in leitor:
            if not (inicio <= linha["dia_prtc"] < fim):
                raise ValueError("Registro fora do periodo")

            valores = [float(linha[c]) for c in FEATURES]

            if not all(math.isfinite(v) for v in valores):
                raise ValueError("Feature invalida no CSV")

            classe = int(linha[TARGET])

            if classe not in (0, 1):
                raise ValueError("Target deve ser 0 ou 1")

            x.append(valores)
            y.append(classe)

    if len(y) < 30:
        raise ValueError("Dados insuficientes para retreino")

    xt, yt, xv, yv = dividir_estratificado(x, y)

    print("Registros:", len(y))
    print("Treinamento:", len(yt))
    print("Validacao:", len(yv))

    print("\n===== 4. TREINANDO O MODELO =====")

    algoritmo = "Regressao logistica - Python puro"

    try:
        import lightgbm as lgb
        from sklearn.metrics import roc_auc_score
    except ImportError:
        print("LightGBM indisponivel: usando modelo local em Python puro.")

        probs, modelo, arquivo_modelo = regressao_logistica(
            xt, yt, xv
        )
    else:
        print("LightGBM encontrado.")

        modelo = lgb.LGBMClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
            objective="binary",
            verbosity=-1
        )

        modelo.fit(xt, yt)

        probs = modelo.predict_proba(xv)[:, 1].tolist()

        algoritmo = "LightGBM"
        arquivo_modelo = "modelo_lightgbm.txt"

    print("\n===== 5. AVALIACAO =====")

    auc = auc_binaria(yv, probs)
    limite_auc = 0.55

    resultado.update(
        status="AVALIADO",
        retreino_executado=True,
        modelo=algoritmo,
        registros=len(y),
        treino=len(yt),
        validacao=len(yv),
        auc=round(auc, 6),
        auc_minima=limite_auc
    )

    print(f"AUC: {auc:.6f}")

    if not math.isfinite(auc) or auc < limite_auc:
        resultado.update(
            status="REPROVADO",
            champion_alterado=False,
            motivo="AUC abaixo do limite"
        )
        salvar_json(
            destino / "RESULTADO_RETREINO.json", resultado
        )
        print("Modelo reprovado. Champion preservado.")
        return resultado

    print("\n===== 6. REGISTRO DO MODELO =====")

    versao = f"v{len(registro['modelos']) + 1:04d}"

    pasta_modelo = destino / "modelos" / versao

    if pasta_modelo.exists():
        raise FileExistsError(
            "A versao ja existe. Nada sera sobrescrito."
        )

    pasta_modelo.mkdir(parents=True)

    if arquivo_modelo.endswith(".json"):
        salvar_json(
            pasta_modelo / arquivo_modelo, modelo
        )
    else:
        modelo.booster_.save_model(
            str(pasta_modelo / arquivo_modelo)
        )

    salvar_json(
        pasta_modelo / "metricas.json",
        {**resultado, "versao": versao}
    )

    registro["modelos"].append({
        "versao": versao,
        "modelo": algoritmo,
        "auc": round(auc, 6),
        "periodo": [inicio, fim],
        "arquivo": str(pasta_modelo / arquivo_modelo)
    })

    registro["champion"] = versao
    registro["execucoes"][chave] = versao

    salvar_json(registro_arquivo, registro)

    resultado.update(
        status="CONCLUIDO",
        versao=versao,
        champion_alterado=True,
        champion=versao,
        motivo="Drift detectado e AUC aprovada"
    )

    salvar_json(
        destino / "RESULTADO_RETREINO.json", resultado
    )

    print("VERSAO REGISTRADA:", versao)
    print("CHAMPION LOCAL:", versao)

    return resultado


def selftest():
    assert auc_binaria(
        [0, 0, 1, 1],
        [0.1, 0.2, 0.8, 0.9]
    ) == 1.0

    assert auc_binaria(
        [0, 1],
        [0.5, 0.5]
    ) == 0.5

    teste_x = [[float(i)] * 12 for i in range(10)]
    teste_y = [0] * 5 + [1] * 5

    _, _, _, yv = dividir_estratificado(
        teste_x, teste_y
    )

    assert len(yv) == 4
    assert set(yv) == {0, 1}

    print("AUTO-TESTES: AUC e divisao estratificada OK")


if __name__ == "__main__":
    selftest()

    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        sys.exit(0)

    if len(sys.argv) != 5:
        raise SystemExit(
            "Uso: arquivo.py ORIGEM DESTINO INICIO FIM"
        )

    resultado = executar(
        Path(sys.argv[1]),
        Path(sys.argv[2]),
        sys.argv[3],
        sys.argv[4]
    )

    print("\n===== RESULTADO DA AULA =====")
    print(
        json.dumps(
            resultado,
            indent=2,
            ensure_ascii=False
        )
    )