# Serialização para retorno (removendo dados sensíveis)
def serialize_user(user):
    return {
        "email": user.get("email"),
        "name": user.get("name"),
        "address": user.get("address"),
        "role": user.get("role", "cliente")
    }
