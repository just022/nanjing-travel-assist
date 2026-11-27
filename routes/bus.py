# routes/bus.py
from flask import Blueprint, render_template, request, abort
from services import bus_service

bus_bp = Blueprint("bus", __name__, url_prefix="/bus")


@bus_bp.route('/')
def bus_index():
    keyword = request.args.get("keyword", "").strip()
    lines = bus_service.search_bus_lines(keyword) if keyword else bus_service.get_all_bus_lines()
    return render_template("bus.html", lines=lines, keyword=keyword)


@bus_bp.route('/<int:line_id>')
def bus_detail(line_id):
    line, stations = bus_service.get_bus_detail(line_id)
    if not line:
        abort(404)
    return render_template("bus_detail.html", line=line, stations=stations)
