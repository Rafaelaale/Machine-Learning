from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.auth_service import login_user
from models.user_model import serialize_user

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET"])
def login_page():
    return render_template("login.html")

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.form
    user = login_user(data["email"], data["password"])
    if not user:
        flash("Credenciais inválidas")
        return redirect(url_for("auth.login_page"))
    
    session["user"] = serialize_user(user)
    return redirect(url_for("auth.dashboard"))

@auth_bp.route("/register", methods=["GET"])
def register_page():
    # Redirect to user-service for user creation
    return redirect("http://localhost:5001/user/create")

@auth_bp.route("/dashboard")
def dashboard():
    user = session.get("user")
    if not user:
        return redirect(url_for("auth.login_page"))
    return render_template("dashboard.html", user=user)

@auth_bp.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("auth.login_page"))
