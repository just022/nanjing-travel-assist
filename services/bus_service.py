# services/bus_service.py
from models.bus import BusLine


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
