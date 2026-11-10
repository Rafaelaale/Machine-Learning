from flask import Blueprint, request, render_template, redirect, url_for, flash, jsonify
from services.product_service import (
    get_all_products, get_available_products, get_products_by_category,
    get_product_by_id, create_product, update_product, delete_product,
    get_categories, initialize_products
)

product_bp = Blueprint("product", __name__)

# Initialize products on startup
initialize_products()

@product_bp.route("/list")
def list_products():
    """Lista todos os produtos disponíveis"""
    products = get_available_products()
    categories = get_categories()
    category_filter = request.args.get('category')
    
    if category_filter:
        products = get_products_by_category(category_filter)
    
    return render_template("product_list.html", products=products, categories=categories, selected_category=category_filter)

@product_bp.route("/admin")
def admin_products():
    """Lista todos os produtos para administração"""
    products = get_all_products()
    categories = get_categories()
    return render_template("admin_products.html", products=products, categories=categories)

@product_bp.route("/create", methods=["GET", "POST"])
def create():
    """Cria um novo produto"""
    if request.method == "POST":
        data = request.form
        ingredients = [ing.strip() for ing in data["ingredients"].split(",") if ing.strip()]
        available = data.get("available") == "on"
        
        response, status = create_product(
            name=data["name"],
            description=data["description"],
            category=data["category"],
            price=data["price"],
            ingredients=ingredients,
            available=available
        )
        
        if status != 201:
            flash(response["error"])
            return redirect(url_for("product.create"))
        
        flash("Produto criado com sucesso!")
        return redirect(url_for("product.admin_products"))
    
    categories = get_categories()
    return render_template("create_product.html", categories=categories)

@product_bp.route("/edit/<product_id>", methods=["GET", "POST"])
def edit(product_id):
    """Edita um produto existente"""
    product = get_product_by_id(product_id)
    if not product:
        flash("Produto não encontrado.")
        return redirect(url_for("product.admin_products"))
    
    if request.method == "POST":
        data = request.form
        ingredients = [ing.strip() for ing in data["ingredients"].split(",") if ing.strip()]
        available = data.get("available") == "on"
        
        success = update_product(
            product_id=product_id,
            name=data["name"],
            description=data["description"],
            category=data["category"],
            price=data["price"],
            ingredients=ingredients,
            available=available
        )
        
        if success:
            flash("Produto atualizado com sucesso!")
        else:
            flash("Erro ao atualizar produto.")
        
        return redirect(url_for("product.admin_products"))
    
    categories = get_categories()
    return render_template("edit_product.html", product=product, categories=categories)

@product_bp.route("/delete/<product_id>", methods=["POST"])
def delete(product_id):
    """Deleta um produto"""
    success = delete_product(product_id)
    if success:
        flash("Produto excluído com sucesso!")
    else:
        flash("Erro ao excluir produto.")
    
    return redirect(url_for("product.admin_products"))

@product_bp.route("/details/<product_id>")
def details(product_id):
    """Mostra detalhes de um produto"""
    product = get_product_by_id(product_id)
    if not product:
        flash("Produto não encontrado.")
        return redirect(url_for("product.list_products"))
    
    return render_template("product_details.html", product=product)

@product_bp.route("/api/products")
def api_products():
    """API endpoint para obter produtos (para integração com outros serviços)"""
    category = request.args.get('category')
    if category:
        products = get_products_by_category(category)
    else:
        products = get_available_products()
    
    return jsonify(products)

@product_bp.route("/api/categories")
def api_categories():
    """API endpoint para obter categorias"""
    categories = get_categories()
    return jsonify(categories)
