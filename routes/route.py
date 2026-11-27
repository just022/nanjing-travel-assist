# routes/route.py
from flask import Blueprint, render_template, request, session
from services import route_service

route_bp = Blueprint("route", __name__, url_prefix="/route")


@route_bp.route('/')
def route_index():
    city_code = request.args.get("city", "nanjing") or "nanjing"
    origin = request.args.get("origin", "").strip()
    destination = request.args.get("destination", "").strip()

    cities = route_service.get_cities()
    available = route_service.city_available(city_code)
    stations = route_service.all_station_names(city_code) if available else []

    result = None
    if available and (origin or destination):
        result = route_service.plan_route(origin, destination, city_code=city_code)

    return render_template(
        "route.html",
        result=result,
        stations=stations,
        cities=cities,
        city_code=city_code,
        available=available,
        origin=origin,
        destination=destination,
        logged_in=session.get("user_id") is not None,
    )
