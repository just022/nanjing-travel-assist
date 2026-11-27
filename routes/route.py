# routes/route.py
from flask import Blueprint, render_template

route_bp = Blueprint("route", __name__, url_prefix="/route")


@route_bp.route('/')
def route_index():
    return render_template("route.html")
