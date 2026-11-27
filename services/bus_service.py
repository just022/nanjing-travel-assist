# services/bus_service.py
from models.bus import BusLine, BusStation


def get_all_bus_lines():
    """获取全部公交线路。"""
    return BusLine.query.order_by(BusLine.id).all()


def search_bus_lines(keyword):
    """按线路名模糊搜索。"""
    if not keyword:
        return []
    return BusLine.query.filter(
        BusLine.line_name.like(f"%{keyword}%")
    ).order_by(BusLine.line_name).all()


def get_bus_detail(line_id):
    """获取单条线路及其站点序列。"""
    line = BusLine.query.get(line_id)
    if not line:
        return None, []
    stations = BusStation.query.filter_by(line_id=line_id).order_by(BusStation.sort).all()
    return line, [s.station_name for s in stations]
