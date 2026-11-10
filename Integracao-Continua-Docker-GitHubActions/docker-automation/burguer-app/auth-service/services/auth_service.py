from werkzeug.security import check_password_hash
from config.database import get_db
from utils.jwt_handler import generate_token

db = get_db()
users_col = db["users"]

def login_user(email, password):
    user = users_col.find_one({"email": email})
    if not user or not check_password_hash(user["password"], password):
        return None
    token = generate_token(user["email"], user["role"])
    # Retorna token e os dados do usuário para a sessão
    return {
        "email": user["email"],
        "name": user.get("name", ""),
        "address": user.get("address", ""),
        "role": user.get("role", "cliente"),
        "token": token
    }
