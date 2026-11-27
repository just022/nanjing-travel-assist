# models/spot.py
from . import db


class ScenicSpot(db.Model):
    __tablename__ = "scenic_spot"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    spot_name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200))
    recommend_traffic = db.Column(db.String(300), comment="推荐出行方式")
    image = db.Column(db.String(200), comment="主配图文件名，存于 static/images")
    images = db.Column(db.String(500), comment="图集文件名，逗号分隔，含主图与辅图")
    description = db.Column(db.Text, comment="图文介绍")
    open_time = db.Column(db.String(100), comment="开放时间")
    ticket = db.Column(db.String(100), comment="门票信息")
    duration = db.Column(db.String(50), comment="建议游玩时长")
    tags = db.Column(db.String(200), comment="亮点标签，逗号分隔")

    def to_dict(self):
        return {
            "id": self.id,
            "spot_name": self.spot_name,
            "address": self.address,
            "recommend_traffic": self.recommend_traffic,
            "image": self.image,
            "images": self.images,
            "description": self.description,
            "open_time": self.open_time,
            "ticket": self.ticket,
            "duration": self.duration,
            "tags": self.tags,
        }
