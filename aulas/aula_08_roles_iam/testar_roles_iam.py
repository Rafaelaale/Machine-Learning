from pathlib import Path
from fnmatch import fnmatchcase
import json

BASE = Path(__file__).resolve().parent
BUCKET = "aws-alura-ds22-local"


def carregar(nome):
    return json.loads(
        (BASE / nome).read_text(encoding="utf-8-sig")
    )


def permitido(politica, acao, chave):
    recurso = f"arn:aws:s3:::{BUCKET}/{chave}"

    def combina(regra):
        acoes = regra["Action"]
        recursos = regra["Resource"]

        if isinstance(acoes, str):
            acoes = [acoes]
        if isinstance(recursos, str):
            recursos = [recursos]

        return (
            any(fnmatchcase(acao, a) for a in acoes)
            and any(fnmatchcase(recurso, r) for r in recursos)
        )

    regras = [
        r for r in politica["Statement"]
        if combina(r)
    ]

    if any(r["Effect"] == "Deny" for r in regras):
        return False

    return any(r["Effect"] == "Allow" for r in regras)


def main():
    print("===== AULA 08 - TESTANDO ROLES IAM =====")
    print("Modo: validacao local, sem conexao AWS")

    trust_sm = carregar("trust_sagemaker.json")
    trust_glue = carregar("trust_glue.json")

    sm = carregar("policy_sagemaker_s3.json")
    glue = carregar("policy_glue_s3.json")

    assert (
        trust_sm["Statement"][0]["Principal"]["Service"]
        == "sagemaker.amazonaws.com"
    )
    assert (
        trust_glue["Statement"][0]["Principal"]["Service"]
        == "glue.amazonaws.com"
    )

    testes = [
        ("SageMaker", sm, "s3:GetObject", "raw/heart.csv", True),
        ("SageMaker", sm, "s3:PutObject", "predictions/resultado.csv", True),
        ("SageMaker", sm, "s3:DeleteObject", "raw/heart.csv", False),
        ("SageMaker", sm, "s3:PutObject", "processed/dados.csv", False),
        ("Glue", glue, "s3:GetObject", "raw/heart.csv", True),
        ("Glue", glue, "s3:PutObject", "processed/heart_limpo.csv", True),
        ("Glue", glue, "s3:DeleteObject", "raw/heart.csv", False),
        ("Glue", glue, "s3:PutObject", "predictions/resultado.csv", False),
    ]

    resultados = []

    for servico, politica, acao, chave, esperado in testes:
        obtido = permitido(politica, acao, chave)
        assert obtido == esperado, (
            f"Falha: {servico} | {acao} | {chave}"
        )

        status = "PERMITIDO" if obtido else "NAO CONCEDIDO"
        print(f"{servico}: {acao} em {chave} -> {status}")

        resultados.append({
            "servico": servico,
            "acao": acao,
            "chave": chave,
            "permitido_na_politica": obtido,
            "teste_aprovado": True,
        })

    destino = BASE.parents[1] / "resultados"
    destino.mkdir(parents=True, exist_ok=True)

    arquivo = destino / "aula_08_roles_iam.json"

    arquivo.write_text(
        json.dumps({
            "aula": 8,
            "modo": "simulacao_local",
            "testes": resultados,
            "total_aprovados": len(testes),
            "recursos_aws_criados": 0
        }, indent=4, ensure_ascii=False),
        encoding="utf-8"
    )

    print("\nTRUST POLICIES: 2/2 VALIDADAS")
    print(f"TESTES: {len(testes)}/{len(testes)} APROVADOS")
    print("RELATORIO:", arquivo)
    print("AULA 08 - CONCLUIDA")


if __name__ == "__main__":
    main()
