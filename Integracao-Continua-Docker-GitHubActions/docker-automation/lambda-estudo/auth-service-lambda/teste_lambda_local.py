import json

from lambda_function import lambda_handler


def testar_get():
    evento = {
        "requestContext": {
            "http": {
                "method": "GET"
            }
        }
    }

    resultado = lambda_handler(evento, None)

    assert resultado["statusCode"] == 200

    dados = json.loads(resultado["body"])

    assert dados["status"] == "ok"
    assert dados["metodo"] == "GET"


def testar_post():
    evento = {
        "httpMethod": "POST"
    }

    resultado = lambda_handler(evento, None)

    assert resultado["statusCode"] == 200

    dados = json.loads(resultado["body"])

    assert dados["metodo"] == "POST"


if __name__ == "__main__":
    testar_get()
    testar_post()

    print("TESTES LAMBDA: 2/2 APROVADOS")
