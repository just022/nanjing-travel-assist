# routes/transit.py
# 统一出行板块：地铁 + 公交 合并展示
from flask import Blueprint, render_template, request, abort
from services import subway_service, bus_service

transit_bp = Blueprint("transit", __name__, url_prefix="/transit")


@transit_bp.route('/')
def transit_index():
    tab = request.args.get("tab", "subway")
    keyword = request.args.get("keyword", "").strip()

    # 地铁数据
    subway_lines = subway_service.get_all_lines()
    line_map = subway_service.get_line_map()
    subway_stations = subway_service.search_stations(keyword) if keyword else []

    # 公交数据
    bus_lines = (
        bus_service.search_bus_lines(keyword) if keyword
        else bus_service.get_all_bus_lines()
    )

    return render_template(
        "transit.html",
        tab=tab,
        keyword=keyword,
        subway_lines=subway_lines,
        line_map=line_map,
        subway_stations=subway_stations,
        bus_lines=bus_lines,
    )


@transit_bp.route('/bus/<int:line_id>')
def bus_detail(line_id):
    line, stations = bus_service.get_bus_detail(line_id)
    if not line:
        abort(404)
    return render_template("bus_detail.html", line=line, stations=stations)
