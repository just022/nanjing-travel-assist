# models/subway.py
from . import db


class SubwayLine(db.Model):
    __tablename__ = "subway_line"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    line_name = db.Column(db.String(50), nullable=False, comment="线路名称，如1号线")
    line_color = db.Column(db.String(20), comment="线路颜色")

    stations = db.relationship("SubwayStation", backref="line", lazy=True)


class SubwayStation(db.Model):
    __tablename__ = "subway_station"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    line_id = db.Column(db.Integer, db.ForeignKey("subway_line.id"), nullable=False)
    station_name = db.Column(db.String(50), nullable=False)
    sort = db.Column(db.Integer, nullable=False, comment="站点顺序")
    is_transfer = db.Column(db.SmallInteger, default=0, comment="是否换乘站 1是 0否")
