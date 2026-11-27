# services/subway_service.py
from models import db
from models.subway import SubwayLine, SubwayStation


def get_all_lines():
    """获取全部地铁线路，按 id 排序。"""
    return SubwayLine.query.order_by(SubwayLine.id).all()


def get_stations_by_line(line_id):
    """按线路 id 获取站点，按站点顺序排序。"""
    return SubwayStation.query.filter_by(line_id=line_id).order_by(SubwayStation.sort).all()


def search_stations(keyword):
    """按站点名模糊搜索。"""
    if not keyword:
        return []
    return SubwayStation.query.filter(
        SubwayStation.station_name.like(f"%{keyword}%")
    ).order_by(SubwayStation.station_name).all()
