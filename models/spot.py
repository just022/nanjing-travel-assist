# models/spot.py
from . import db


class ScenicSpot(db.Model):
    __tablename__ = "scenic_spot"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spot_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    recommend_traffic = db.Column(db.String(300), comment="推荐出行方式")
    image = db.Column(db.String(200), comment="配图文件名，存于 static/images")

    def to_dict(self):
        return {
            "id": self.id,
            "spot_name": self.spot_name,
            "address": self.address,
            "recommend_traffic": self.recommend_traffic,
            "image": self.image,
        }
