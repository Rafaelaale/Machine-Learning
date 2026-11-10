import os
import sys
import urllib.request
from pymongo import MongoClient

def main():
    modo = sys.argv[1]

    if modo == "http":
        url = sys.argv[2]
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler({})
        )
        with opener.open(url, timeout=10) as resposta:
            print("HTTP", resposta.status, url)
            if resposta.status != 200:
                sys.exit(1)

    elif modo == "mongo":
        uri = os.environ.get("MONGO_URI")
        if not uri:
            raise RuntimeError("MONGO_URI nao configurada")

        cliente = MongoClient(
            uri,
            serverSelectionTimeoutMS=6000
        )
        resultado = cliente.admin.command("ping")
        print("MONGODB PING:", resultado["ok"])

        if resultado["ok"] != 1:
            sys.exit(1)

    else:
        raise ValueError("Modo de teste desconhecido")

if __name__ == "__main__":
    try:
        main()
    except Exception as erro:
        print("FALHA:", type(erro).__name__, str(erro))
        sys.exit(1)