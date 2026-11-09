import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import numpy as np
import xgboost as xgb

MODEL_NAME = "fraude"
MODEL_PATH = os.environ.get(
    "MODEL_PATH",
    "/models/aula26-20261108210412/model.ubj"
)

booster = xgb.Booster()
booster.load_model(MODEL_PATH)
booster.set_param({"nthread": 1})

FEATURES = booster.num_features()

print(f"MODELO CARREGADO: {MODEL_PATH}", flush=True)
print(f"FEATURES: {FEATURES}", flush=True)


class Handler(BaseHTTPRequestHandler):

    def respond(self, status, obj):
        raw = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = self.path.rstrip("/")

        if path in (
            "/v2/health/live",
            "/v2/health/ready",
            "/v2/models/fraude/ready"
        ):
            return self.respond(200, {})

        if path == "/v2":
            return self.respond(200, {
                "name": "fraude-servidor-compat",
                "version": "1",
                "extensions": []
            })

        if path == "/v2/models":
            return self.respond(200, {"models": [MODEL_NAME]})

        if path == "/v2/models/fraude":
            return self.respond(200, {
                "name": MODEL_NAME,
                "platform": "xgboost",
                "inputs": [{
                    "name": "input-0",
                    "datatype": "FP32",
                    "shape": [-1, FEATURES]
                }],
                "outputs": [{
                    "name": "output-0",
                    "datatype": "FP32",
                    "shape": [-1]
                }]
            })

        self.respond(404, {"error": "Endpoint nao encontrado"})

    def do_POST(self):
        if self.path != "/v2/models/fraude/infer":
            return self.respond(404, {"error": "Endpoint nao encontrado"})

        try:
            tamanho = int(self.headers.get("Content-Length", "0"))

            if tamanho <= 0 or tamanho > 2097152:
                raise ValueError("Tamanho de requisicao invalido")

            body = json.loads(self.rfile.read(tamanho))
            entrada = body["inputs"][0]

            if entrada["datatype"] != "FP32":
                raise ValueError("Datatype deve ser FP32")

            shape = entrada["shape"]

            if (
                len(shape) != 2
                or not 1 <= shape[0] <= 100
                or shape[1] != FEATURES
            ):
                raise ValueError(
                    f"Shape esperado: [n, {FEATURES}], n entre 1 e 100"
                )

            X = np.asarray(
                entrada["data"], dtype=np.float32
            ).reshape(shape)

            if not np.isfinite(X).all():
                raise ValueError("Entrada contem valores invalidos")

            resultado = np.asarray(
                booster.predict(xgb.DMatrix(X)),
                dtype=np.float32
            )

            self.respond(200, {
                "model_name": MODEL_NAME,
                "outputs": [{
                    "name": "output-0",
                    "datatype": "FP32",
                    "shape": list(resultado.shape),
                    "data": resultado.flatten().tolist()
                }]
            })

        except Exception as erro:
            self.respond(400, {"error": str(erro)})


ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
