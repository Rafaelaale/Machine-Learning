from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
import requests
from services.order_service import (
    create_order, get_order_by_id, get_orders_by_user, 
    get_all_orders, update_order_status, delete_order, get_all_users
)

def get_products_from_service():
    """Busca produtos do product-service"""
    try:
        response = requests.get("http://localhost:5003/product/api/products")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Erro ao buscar produtos: {e}")
        return []

def get_categories_from_service():
    """Busca categorias do product-service"""
    try:
        response = requests.get("http://localhost:5003/product/api/categories")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print(f"Erro ao buscar categorias: {e}")
        return []

order_bp = Blueprint("order", __name__)

@order_bp.route("/create", methods=["GET", "POST"])
def create():
    """Página para criar um novo pedido"""
    if request.method == "POST":
        data = request.form
        user_email = data.get("user_email")
        
        # Processa os itens do pedido
        items = []
        total = 0.0
        
        # Exemplo simples - você pode expandir isso
        item_names = request.form.getlist("item_name")
        item_quantities = request.form.getlist("item_quantity")
        item_prices = request.form.getlist("item_price")
        
        for name, qty, price in zip(item_names, item_quantities, item_prices):
            if name and qty and price:
                quantity = int(qty)
                unit_price = float(price)
                item_total = quantity * unit_price
                
                items.append({
                    "name": name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "total": item_total
                })
                total += item_total
        
        if not items:
            flash("Adicione pelo menos um item ao pedido", "error")
            return redirect(url_for("order.create"))
        
        response, status = create_order(user_email, items, total)
        
        if status == 201:
            flash("Pedido criado com sucesso!", "success")
            return redirect(url_for("order.list_orders"))
        elif status == 404:
            flash(response.get("error", "Usuário não encontrado"), "error")
            return redirect(url_for("order.create"))
        else:
            flash(response.get("error", "Erro ao criar pedido"), "error")
            return redirect(url_for("order.create"))
    
    # Get all users for reference in the form
    users = get_all_users()
    
    # Get products from product service
    products = get_products_from_service()
    categories = get_categories_from_service()
    
    return render_template("create_order.html", users=users, products=products, categories=categories)

@order_bp.route("/list")
def list_orders():
    """Lista todos os pedidos"""
    orders = get_all_orders()
    return render_template("order_list.html", orders=orders)

@order_bp.route("/details/<order_id>")
def order_details(order_id):
    """Exibe detalhes de um pedido específico"""
    order = get_order_by_id(order_id)
    if not order:
        flash("Pedido não encontrado", "error")
        return redirect(url_for("order.list_orders"))
    return render_template("order_details.html", order=order)

@order_bp.route("/user/<user_email>")
def user_orders(user_email):
    """Lista pedidos de um usuário específico"""
    orders = get_orders_by_user(user_email)
    return render_template("order_list.html", orders=orders, user_email=user_email)

@order_bp.route("/update_status/<order_id>", methods=["POST"])
def update_status(order_id):
    """Atualiza o status de um pedido"""
    new_status = request.form.get("status")
    if not new_status:
        flash("Status é obrigatório", "error")
        return redirect(url_for("order.order_details", order_id=order_id))
    
    response, status = update_order_status(order_id, new_status)
    
    if status == 200:
        flash("Status atualizado com sucesso!", "success")
    else:
        flash(response.get("error", "Erro ao atualizar status"), "error")
    
    return redirect(url_for("order.order_details", order_id=order_id))

@order_bp.route("/delete/<order_id>", methods=["POST"])
def delete(order_id):
    """Deleta um pedido"""
    response, status = delete_order(order_id)
    
    if status == 200:
        flash("Pedido deletado com sucesso!", "success")
    else:
        flash(response.get("error", "Erro ao deletar pedido"), "error")
    
    return redirect(url_for("order.list_orders"))
