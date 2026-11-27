# services/user_service.py
from models import db
from models.user import User, RouteFavorite


def register(username, password, nickname=None):
    """注册新用户，返回 (用户对象, 提示信息)。"""
    username = (username or "").strip()
    if not username or not password:
        return None, "用户名和密码不能为空"
    if User.query.filter_by(username=username).first():
        return None, "用户名已存在"

    user = User(username=username, nickname=nickname or username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user, "注册成功"


def login(username, password):
    """校验登录，返回 (用户对象, 提示信息)。"""
    username = (username or "").strip()
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return None, "用户名或密码错误"
    return user, "登录成功"


def add_favorite(user_id, origin, destination, summary, path):
    """收藏路线，重复收藏则不重复插入。"""
    exists = RouteFavorite.query.filter_by(
        user_id=user_id, origin=origin, destination=destination
    ).first()
    if exists:
        return False, "该路线已收藏"

    fav = RouteFavorite(
        user_id=user_id,
        origin=origin,
        destination=destination,
        summary=summary,
        path=path,
    )
    db.session.add(fav)
    db.session.commit()
    return True, "收藏成功"


def remove_favorite(fav_id, user_id):
    fav = RouteFavorite.query.filter_by(id=fav_id, user_id=user_id).first()
    if not fav:
        return False, "收藏记录不存在"
    db.session.delete(fav)
    db.session.commit()
    return True, "已取消收藏"


def list_favorites(user_id):
    return RouteFavorite.query.filter_by(user_id=user_id).order_by(
        RouteFavorite.created_at.desc()
    ).all()
