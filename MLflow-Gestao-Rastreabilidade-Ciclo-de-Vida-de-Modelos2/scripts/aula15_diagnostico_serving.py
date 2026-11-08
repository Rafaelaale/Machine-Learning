import traceback
import mlflow
import mlflow.pyfunc
import pandas as pd

uri = "models:/risco_credito_classifier_pyfunc@servingCandidate"

mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_registry_uri("http://127.0.0.1:5000")

try:
    print("CARREGANDO:", uri)
    modelo = mlflow.pyfunc.load_model(uri)
    print("MODELO CARREGADO COM SUCESSO")

    cliente = pd.DataFrame([{
        "idade": 34,
        "renda_mensal": 4200.0,
        "tempo_emprego_anos": 5.0,
        "score_interno": 620,
        "valor_solicitado": 12000.0,
        "num_parcelas": 24,
        "tipo_renda": "CLT",
        "possui_restricao": "nao"
    }])

    resultado = modelo.predict(
        cliente,
        params={"threshold": 0.30}
    )

    print("PREDICAO:")
    print(resultado.to_string(index=False))
    print("DIAGNOSTICO: MODELO FUNCIONAL")

except Exception:
    print("DIAGNOSTICO: FALHA NO CARREGAMENTO OU INFERENCIA")
    traceback.print_exc()
    raise
