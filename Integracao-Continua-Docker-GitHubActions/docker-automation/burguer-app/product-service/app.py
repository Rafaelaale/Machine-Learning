from flask import Flask
from controllers.product_controller import product_bp
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

app.register_blueprint(product_bp, url_prefix='/product')

@app.route('/')
def index():
    return '<a href="/product/list">Ver produtos disponíveis</a>'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5003, debug=True)
