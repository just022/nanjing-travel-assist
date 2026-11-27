# routes/subway.py
from flask import Blueprint, render_template, request
from services import subway_service

subway_bp = Blueprint("subway", __name__, url_prefix="/subway")


@subway_bp.route('/')
def subway_index():
    keyword = request.args.get("keyword", "").strip()
    lines = subway_service.get_all_lines()
    line_map = subway_service.get_line_map()
    stations = subway_service.search_stations(keyword) if keyword else []
    return render_template(
        "subway.html",
        lines=lines,
        line_map=line_map,
        stations=stations,
        keyword=keyword,
    )
