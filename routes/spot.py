# routes/spot.py
from flask import Blueprint, render_template, abort, request
from services import spot_service, recommend_service, route_service

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

    origin = request.args.get("origin", "").strip()
    stations = route_service.all_station_names("nanjing")
    spot_route = None
    if origin:
        spot_route = recommend_service.plan_to_spot(spot.spot_name, origin)

    return render_template(
        "spot_detail.html",
        spot=spot,
        stations=stations,
        origin=origin,
        spot_route=spot_route,
    )
