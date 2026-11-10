from flask import Flask, redirect, url_for
from controllers.order_controller import order_bp
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Cria a instância da aplicação Flask
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Registra o blueprint de pedidos
app.register_blueprint(order_bp, url_prefix='/order')

# Redireciona a rota raiz para a lista de pedidos
@app.route('/')
def index():
    return redirect(url_for('order.list_orders'))

if __name__ == '__main__':
    # Executa a aplicação Flask
    app.run(host="0.0.0.0", port=5002, debug=True)
    # O debug=True permite recarregar automaticamente a aplicação ao fazer alterações no código
