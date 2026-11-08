"""Cliente HTTP independente para testar o serving."""

import json

from src.aula15_serving_rest import (
    chamar_api,
    criar_payload,
    extrair_predicao,
)


for threshold in (0.30, 0.40, 0.50):
    resposta = chamar_api(
        criar_payload(threshold)
    )

    print("\nTHRESHOLD:", threshold)
    print("HTTP:", resposta["status_code"])

    print(
        json.dumps(
            extrair_predicao(resposta),
            ensure_ascii=False,
            indent=2,
        )
    )


resposta = chamar_api(
    criar_payload(
        0.30,
        remover_coluna="score_interno",
    )
)

print("\nPAYLOAD INVALIDO")
print("HTTP:", resposta["status_code"])
print(
    json.dumps(
        resposta["body"],
        ensure_ascii=False,
        indent=2,
    )[:1500]
)
