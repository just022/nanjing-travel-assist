# routes/main.py
from flask import Blueprint, render_template
from services import spot_service

main_bp = Blueprint("main", __name__)


@main_bp.route('/')
def index():
    spots = spot_service.get_all_spots()[:4]
    return render_template("index.html", spots=spots)
