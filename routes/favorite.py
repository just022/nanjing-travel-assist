# routes/favorite.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from services import user_service

favorite_bp = Blueprint("favorite", __name__, url_prefix="/favorite")


@favorite_bp.route("/")
def index():
    user_id = session.get("user_id")
    if not user_id:
        flash("请先登录后再查看收藏路线")
        return redirect(url_for("auth.login"))
    favs = user_service.list_favorites(user_id)
    return render_template("favorites.html", favs=favs)


@favorite_bp.route("/add", methods=["POST"])
def add():
    user_id = session.get("user_id")
    if not user_id:
        flash("请先登录后再收藏路线")
        return redirect(url_for("auth.login"))

    origin = request.form.get("origin", "").strip()
    destination = request.form.get("destination", "").strip()
    summary = request.form.get("summary", "").strip()
    path = request.form.get("path", "").strip()

    _, msg = user_service.add_favorite(user_id, origin, destination, summary, path)
    flash(msg)
    return redirect(url_for("route.route_index", origin=origin, destination=destination))


@favorite_bp.route("/remove/<int:fav_id>")
def remove(fav_id):
    user_id = session.get("user_id")
    if not user_id:
        return redirect(url_for("auth.login"))
    _, msg = user_service.remove_favorite(fav_id, user_id)
    flash(msg)
    return redirect(url_for("favorite.index"))
