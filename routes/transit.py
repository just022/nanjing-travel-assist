# routes/transit.py
# 兼容旧入口：出行查询已并入「出行规划」板块，这里做重定向；公交详情保留独立页。
from flask import Blueprint, render_template, abort, redirect, request
from services import bus_service, spot_service

transit_bp = Blueprint("transit", __name__, url_prefix="/transit")


@transit_bp.route('/')
def transit_index():
    # 旧 /transit/ 入口跳转到合并板块的线路查询页签
    tab = request.args.get("tab", "subway")
    transit = "bus" if tab == "bus" else "subway"
    return redirect(__import__("flask").url_for("route.route_index", tab="query", transit=transit))


@transit_bp.route('/bus/<int:line_id>')
def bus_detail(line_id):
    line, stations = bus_service.get_bus_detail(line_id)
    if not line:
        abort(404)
    station_spots = spot_service.station_to_spots()
    return render_template("bus_detail.html", line=line, stations=stations,
                           station_spots=station_spots)
