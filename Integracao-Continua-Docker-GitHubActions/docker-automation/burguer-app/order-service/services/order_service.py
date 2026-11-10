from config.database import get_db
from models.order_model import serialize_order
from datetime import datetime
from bson import ObjectId

db = get_db()
orders_col = db["orders"]
users_col = db["users"]  # Add reference to users collection

def create_order(user_email, items, total):
    """Cria um novo pedido no banco de dados"""
    # Validate that user exists
    user = users_col.find_one({"email": user_email})
    if not user:
        return {"error": f"Usuário com email '{user_email}' não encontrado. Verifique se o email está correto."}, 404
    
    order = {
        "user_email": user_email,
        "user_id": str(user["_id"]),  # Store user reference for future use
        "items": items,
        "total": total,
        "status": "pending",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    result = orders_col.insert_one(order)
    return {"message": "Pedido criado com sucesso", "order_id": str(result.inserted_id)}, 201

def get_order_by_id(order_id):
    """Busca um pedido pelo ID"""
    try:
        order = orders_col.find_one({"_id": ObjectId(order_id)})
        if order:
            return serialize_order(order)
        return None
    except:
        return None

def get_orders_by_user(user_email):
    """Busca todos os pedidos de um usuário"""
    orders = orders_col.find({"user_email": user_email}).sort("created_at", -1)
    return [serialize_order(order) for order in orders]

def get_all_orders():
    """Busca todos os pedidos"""
    orders = orders_col.find().sort("created_at", -1)
    return [serialize_order(order) for order in orders]

def update_order_status(order_id, status):
    """Atualiza o status de um pedido"""
    try:
        result = orders_col.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )
        if result.modified_count > 0:
            return {"message": "Status do pedido atualizado com sucesso"}, 200
        return {"error": "Pedido não encontrado"}, 404
    except:
        return {"error": "ID de pedido inválido"}, 400

def get_all_users():
    """Busca todos os usuários cadastrados para referência"""
    users = users_col.find({}, {"email": 1, "name": 1, "_id": 0}).sort("email", 1)
    return list(users)

def delete_order(order_id):
    """Deleta um pedido"""
    try:
        result = orders_col.delete_one({"_id": ObjectId(order_id)})
        if result.deleted_count > 0:
            return {"message": "Pedido deletado com sucesso"}, 200
        return {"error": "Pedido não encontrado"}, 404
    except:
        return {"error": "ID de pedido inválido"}, 400
