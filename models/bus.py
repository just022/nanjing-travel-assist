# models/bus.py
from . import db


class BusLine(db.Model):
    __tablename__ = "bus_line"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    line_name = db.Column(db.String(50), nullable=False)
    start_station = db.Column(db.String(50))
    end_station = db.Column(db.String(50))
    stations = db.Column(db.Text, comment="途经站点，逗号分隔")
    first_time = db.Column(db.String(20), comment="首班车时间")
    last_time = db.Column(db.String(20), comment="末班车时间")


class BusStation(db.Model):
    __tablename__ = "bus_station"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    line_id = db.Column(db.Integer, db.ForeignKey("bus_line.id"), nullable=False)
    station_name = db.Column(db.String(50), nullable=False)
    sort = db.Column(db.Integer, nullable=False)

