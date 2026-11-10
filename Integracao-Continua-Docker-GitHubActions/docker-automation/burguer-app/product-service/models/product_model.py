# Serialização para retorno de produtos
def serialize_product(product):
    return {
        "id": str(product.get("_id")),
        "name": product.get("name"),
        "description": product.get("description"),
        "category": product.get("category"),
        "price": product.get("price"),
        "available": product.get("available", True),
        "ingredients": product.get("ingredients", [])
    }
