# routes/spot.py
from flask import Blueprint, render_template, abort
from services import spot_service

spot_bp = Blueprint("spot", __name__, url_prefix="/spot")


@spot_bp.route('/')
def spot_index():
    spots = spot_service.get_all_spots()
    return render_template("spot.html", spots=spots)


@spot_bp.route('/<int:spot_id>')
def spot_detail(spot_id):
    spot = spot_service.get_spot_detail(spot_id)
    if not spot:
        abort(404)
    return render_template("spot_detail.html", spot=spot)
