# models/bus.py
from . import db


class BusLine(db.Model):
    __tablename__ = "bus_line"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    line_name = db.Column(db.String(50), nullable=False)
    start_station = db.Column(db.String(50))
    end_station = db.Column(db.String(50))
