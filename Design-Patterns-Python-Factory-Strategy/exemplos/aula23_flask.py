"""Exemplo da transcricao - Flask.

Requer Flask somente quando este arquivo for executado.
"""

from flask import Flask

app = Flask(__name__)


@app.route("/home")
def home():
    return "Olá!"


if __name__ == "__main__":
    app.run(debug=False)
