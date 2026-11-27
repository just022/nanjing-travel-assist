# routes/spot.py
from flask import Blueprint, render_template
from services import spot_service

spot_bp = Blueprint("spot", __name__, url_prefix="/spot")


@spot_bp.route('/')
def spot_index():
    spots = spot_service.get_all_spots()
    return render_template("spot.html", spots=spots)
