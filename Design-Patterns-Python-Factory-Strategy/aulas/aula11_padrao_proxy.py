"""Laboratorio da Aula 11 - Padrao Proxy."""

import json
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.aula11_padrao_proxy import (
    Config,
    ConfigProxy,
    ConfigProxyLazyLoading,
    DataProxy,
    ExemploProperty,
    demonstrar_partial,
)


def main():
    print("===== AULA 11 - PADRAO PROXY =====")

    print("\n1. OBJETO REAL")
    real = Config()

    print("Tema:", real.data["theme"])
    print("Idioma:", real.data["language"])
    print("Leituras:", real.leituras)

    print("\n2. CONFIGPROXY - LAZY LOADING")
    proxy = ConfigProxy()

    print("Aplicação iniciada.")
    print(
        "Objeto real antes do acesso:",
        proxy._config is not None,
    )

    print("Tema configurado:", proxy.data["theme"])
    print("Idioma configurado:", proxy.data["language"])
    print(
        "Leituras:",
        proxy._config.leituras,
    )

    print("\n3. PROXY COM LOGGING")
    logging_proxy = ConfigProxyLazyLoading()

    print("Aplicação iniciada.")

    print(
        "Tema configurado:",
        logging_proxy.data["theme"],
    )
    print(
        "Idioma configurado:",
        logging_proxy.data["language"],
    )

    print("\n4. DATAPROXY - ACESSO POR CHAVE")
    dados_proxy = DataProxy(logging_proxy)

    print("Tema via DataProxy:", dados_proxy["theme"])
    print("Idioma via DataProxy:", dados_proxy["language"])
    print(
        "Chave inexistente:",
        dados_proxy["inexistente"],
    )

    print(
        "Chaves registradas:",
        dados_proxy.chaves_acessadas,
    )

    print(
        "Leituras do JSON:",
        logging_proxy._config.leituras,
    )

    print("\n5. PROPERTY")
    print("ExemploProperty().x:", ExemploProperty().x)

    print("\n6. FUNCTOOLS.PARTIAL")
    exemplos_partial = demonstrar_partial()

    print(json.dumps(
        exemplos_partial,
        indent=2,
        ensure_ascii=False,
    ))

    relatorio = {
        "aula": 11,
        "titulo": "Padrao Proxy",
        "objeto_real": {
            "tema": real.data["theme"],
            "idioma": real.data["language"],
            "leituras": real.leituras,
        },
        "proxy": {
            "tema": proxy.data["theme"],
            "idioma": proxy.data["language"],
            "leituras": proxy._config.leituras,
        },
        "logging_proxy": {
            "leituras": logging_proxy._config.leituras,
            "chaves_acessadas": dados_proxy.chaves_acessadas,
        },
        "property": ExemploProperty().x,
        "partial": exemplos_partial,
    }

    assert real.data["theme"] == "ARC"
    assert real.data["language"] == "PT-BR"

    assert proxy._config.leituras == 1
    assert logging_proxy._config.leituras == 1

    assert exemplos_partial["plus_10_com_5"] == 15
    assert exemplos_partial["plus_5_com_10"] == 15

    destino = (
        BASE / "resultados"
        / "aula11_padrao_proxy.json"
    )

    destino.parent.mkdir(
        parents=True, exist_ok=True
    )

    destino.write_text(
        json.dumps(
            relatorio,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("\nRELATORIO:", destino)
    print("AULA 11 EXECUTADA COM SUCESSO!")


if __name__ == "__main__":
    main()
