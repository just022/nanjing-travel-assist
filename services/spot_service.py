# services/spot_service.py
from collections import defaultdict
from models.spot import ScenicSpot


def get_all_spots():
    """获取全部南京景点。"""
    return ScenicSpot.query.order_by(ScenicSpot.id).all()


def get_spot_detail(spot_id):
    """根据 id 获取单个景点。"""
    return ScenicSpot.query.get(spot_id)


def station_to_spots():
    """返回 {最近站点名: [景点对象...]} 映射，供出行查询站点标注可去景点。"""
    mapping = defaultdict(list)
    for spot in ScenicSpot.query.order_by(ScenicSpot.id).all():
        if spot.nearest_station:
            mapping[spot.nearest_station].append(spot)
    return dict(mapping)


def spots_at_station(station_name):
    """返回某站点可达的景点列表（无则空列表）。"""
    if not station_name:
        return []
    return ScenicSpot.query.filter_by(nearest_station=station_name).order_by(ScenicSpot.id).all()
