from flask import Flask
from controllers.user_controller import user_bp
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

app.register_blueprint(user_bp, url_prefix='/user')

@app.route('/')
def index():
    return '<a href="/user/create">Cadastrar novo usuário</a>'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
