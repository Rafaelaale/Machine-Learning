# Serialização para retorno de pedidos (removendo dados sensíveis)
def serialize_order(order):
    # Helper function to format datetime
    def format_datetime(dt):
        if dt and hasattr(dt, 'strftime'):
            return dt.strftime('%d/%m/%Y %H:%M')
        return None
    
    return {
        "id": str(order["_id"]),
        "user_email": order.get("user_email"),
        "user_id": order.get("user_id"),  # Include user reference
        "items": order.get("items", []),
        "total": order.get("total", 0.0),
        "status": order.get("status", "pending"),
        "created_at": order.get("created_at"),
        "updated_at": order.get("updated_at"),
        "created_at_formatted": format_datetime(order.get("created_at")),
        "updated_at_formatted": format_datetime(order.get("updated_at"))
    }
