# routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services import user_service

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        nickname = request.form.get("nickname", "")
        user, msg = user_service.register(username, password, nickname)
        if user:
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("main.index"))
        flash(msg)
    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        user, msg = user_service.login(username, password)
        if user:
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("main.index"))
        flash(msg)
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.index"))
