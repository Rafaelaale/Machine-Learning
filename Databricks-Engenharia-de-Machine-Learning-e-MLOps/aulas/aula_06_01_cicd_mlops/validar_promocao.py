import argparse


def autorizado(origem, destino):
    return (origem, destino) in {
        ("develop", "stage"),
        ("stage", "main"),
    }


def autoteste():
    casos = [
        ("develop", "stage", True),
        ("stage", "main", True),
        ("develop", "main", False),
        ("feature/novo", "main", False),
        ("feature/novo", "stage", False),
        ("main", "stage", False),
    ]

    for origem, destino, esperado in casos:
        obtido = autorizado(origem, destino)

        assert obtido is esperado, (
            f"Falha: {origem} -> {destino}"
        )

        status = "PERMITIDO" if obtido else "BLOQUEADO"

        print(f"{status}: {origem} -> {destino}")

    print("TESTES DAS BRANCHES: OK")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--origem")
    parser.add_argument("--destino")

    args = parser.parse_args()

    if args.self_test:
        autoteste()
    else:
        if not args.origem or not args.destino:
            parser.error("Informe origem e destino")

        if autorizado(args.origem, args.destino):
            print(
                f"PROMOCAO AUTORIZADA: "
                f"{args.origem} -> {args.destino}"
            )
        else:
            parser.exit(
                1,
                f"PROMOCAO BLOQUEADA: "
                f"{args.origem} -> {args.destino}\n"
            )