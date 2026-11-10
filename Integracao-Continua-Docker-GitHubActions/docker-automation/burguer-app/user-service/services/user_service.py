from config.database import get_db
from werkzeug.security import generate_password_hash
from models.user_model import serialize_user

db = get_db()
users_col = db["users"]

def create_user(email, password, name, address, role="cliente"):
    # Verifica se email já existe
    if users_col.find_one({"email": email}):
        return {"error": "Usuário já existe"}, 400

    hashed_pw = generate_password_hash(password)
    user = {
        "email": email,
        "password": hashed_pw,
        "name": name,
        "address": address,
        "role": role
    }
    users_col.insert_one(user)
    return {"message": "Usuário criado com sucesso"}, 201

def get_user_by_email(email):
    user = users_col.find_one({"email": email})
    if user:
        return serialize_user(user)
    return None

def update_user(email, name, address):
    users_col.update_one(
        {"email": email},
        {"$set": {"name": name, "address": address}}
    )

def delete_user(email):
    users_col.delete_one({"email": email})
