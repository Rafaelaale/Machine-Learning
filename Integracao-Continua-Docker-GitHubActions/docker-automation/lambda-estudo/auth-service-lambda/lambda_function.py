import json


def lambda_handler(event, context):
    """
    Funcao Lambda independente para estudo.

    Nao executa o Flask auth-service original.
    """

    method = "GET"

    if isinstance(event, dict):
        method = event.get("httpMethod", "GET")

        request_context = event.get("requestContext") or {}
        http_context = request_context.get("http") or {}

        method = http_context.get("method") or method

    resposta = {
        "status": "ok",
        "servico": "auth-service-lambda-demo",
        "metodo": method
    }

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(resposta)
    }
