"""Helpers para o pipeline de cotação USD-BRL."""

import json
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import requests


def buscar_cotacao(url: str) -> dict:
    """Busca a cotação USD-BRL na AwesomeAPI.

    Args:
        url: endpoint da AwesomeAPI para USD-BRL.

    Returns:
        Dicionário com os dados da cotação.

    Raises:
        requests.HTTPError: se a API retornar erro.
        ValueError: se a resposta não contiver os campos esperados.
    """
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    dados = response.json()

    if "USDBRL" not in dados:
        raise ValueError("Resposta da API não contém o campo USDBRL")

    cotacao = dados["USDBRL"]
    campos_obrigatorios = ["bid", "ask", "high", "low", "create_date"]

    for campo in campos_obrigatorios:
        if campo not in cotacao:
            raise ValueError(f"Campo obrigatório ausente na resposta: {campo}")

    return cotacao


def salvar_json_bruto(cotacao: dict, pasta_destino: str) -> str:
    """Salva o JSON bruto da cotação.

    Args:
        cotacao: dicionário retornado pela API.
        pasta_destino: pasta onde o JSON será salvo.

    Returns:
        Caminho completo do arquivo salvo.
    """
    Path(pasta_destino).mkdir(parents=True, exist_ok=True)

    data_str = datetime.now().strftime("%Y-%m-%d")
    caminho = Path(pasta_destino) / f"cotacao_{data_str}.json"

    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(cotacao, f, ensure_ascii=False, indent=2)

    return str(caminho)


def consolidar_historico(pasta_raw: str, caminho_consolidado: str) -> str:
    """Consolida os últimos 7 dias de cotação em um único CSV.

    Args:
        pasta_raw: pasta com os JSONs brutos diários.
        caminho_consolidado: caminho do CSV consolidado final.

    Returns:
        Caminho do arquivo consolidado.
    """
    hoje = datetime.now().date()
    datas_validas = {
        (hoje - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)
    }

    registros = []
    pasta = Path(pasta_raw)

    for arquivo in sorted(pasta.glob("cotacao_*.json")):
        data_arquivo = arquivo.stem.replace("cotacao_", "")
        if data_arquivo not in datas_validas:
            continue

        with open(arquivo, "r", encoding="utf-8") as f:
            dados = json.load(f)

        registros.append({
            "data": data_arquivo,
            "abertura": float(dados.get("bid", 0)),
            "maxima": float(dados.get("high", 0)),
            "minima": float(dados.get("low", 0)),
            "fechamento": float(dados.get("ask", 0)),
        })

    df = pd.DataFrame(registros)
    df = df.sort_values("data")

    Path(caminho_consolidado).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(caminho_consolidado, index=False)

    return caminho_consolidado
