# services/spot_service.py
from models.spot import ScenicSpot


def get_all_spots():
    """获取全部南京景点。"""
    return ScenicSpot.query.order_by(ScenicSpot.id).all()


def get_spot_detail(spot_id):
    """根据 id 获取单个景点。"""
    return ScenicSpot.query.get(spot_id)
