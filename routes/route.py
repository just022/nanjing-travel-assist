# routes/route.py
from flask import Blueprint, render_template, request
from services import route_service

route_bp = Blueprint("route", __name__, url_prefix="/route")


@route_bp.route('/')
def route_index():
    origin = request.args.get("origin", "").strip()
    destination = request.args.get("destination", "").strip()
    result = None
    stations = route_service.all_station_names()

    if origin or destination:
        result = route_service.plan_route(origin, destination)

    return render_template(
        "route.html",
        result=result,
        stations=stations,
        origin=origin,
        destination=destination,
    )
