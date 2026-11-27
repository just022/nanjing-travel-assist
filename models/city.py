# models/city.py
from . import db


class City(db.Model):
    """
    城市字典表：后续接入其他热门城市时，在此新增记录即可。
    现有地铁/公交/景点数据均归属南京（city_code = 'nanjing'）。
    """
    __tablename__ = "city"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(30), unique=True, nullable=False, comment="城市编码，如 nanjing")
    name = db.Column(db.String(50), nullable=False, comment="城市名称")
    enabled = db.Column(db.SmallInteger, default=1, comment="是否已收录数据 1是 0否")

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "enabled": bool(self.enabled),
        }
