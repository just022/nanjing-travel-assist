# routes/route.py
from flask import Blueprint, render_template, request, session
from services import route_service, recommend_service, makeup_service

route_bp = Blueprint("route", __name__, url_prefix="/route")


@route_bp.route('/')
def route_index():
    city_code = request.args.get("city", "nanjing") or "nanjing"
    origin = request.args.get("origin", "").strip()
    destination = request.args.get("destination", "").strip()

    # 需求推荐参数
    prefs = request.args.getlist("pref")
    duration_bucket = request.args.get("duration", "半天")
    mode = request.args.get("mode", "recommend")  # recommend: 需求推荐; manual: 自选路线

    cities = route_service.get_cities()
    available = route_service.city_available(city_code)
    stations = route_service.all_station_names(city_code) if available else []

    # 自选路线结果
    manual_result = None
    if available and (origin or destination):
        manual_result = route_service.plan_route(origin, destination, city_code=city_code)

    # 需求推荐结果
    recommendations = []
    itinerary = None
    weather = None
    if mode == "recommend" and available:
        weather = makeup_service.get_nanjing_weather()
        user_id = session.get("user_id")
        scored = recommend_service.recommend_spots(
            preferences=prefs,
            duration_bucket=duration_bucket,
            weather=weather,
            user_id=user_id,
            origin=origin,
            city_code=city_code,
        )
        # 按时长把靠前景点串成一条一日游动线
        itinerary = recommend_service.build_itinerary(
            scored, origin, city_code=city_code, duration_bucket=duration_bucket,
        )
        for item, leg in zip(itinerary["spots"], itinerary["legs"]):
            recommendations.append({
                "spot": item["spot"],
                "score": item["score"],
                "reasons": item["reasons"],
                "tags": item["tags"],
                "route": leg,
            })

    return render_template(
        "route.html",
        mode=mode,
        result=manual_result,
        stations=stations,
        cities=cities,
        city_code=city_code,
        available=available,
        origin=origin,
        destination=destination,
        prefs=prefs,
        duration_bucket=duration_bucket,
        preferences=recommend_service.preference_options(),
        recommendations=recommendations,
        itinerary=itinerary,
        weather=weather,
        logged_in=session.get("user_id") is not None,
    )
