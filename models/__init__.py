# models/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .subway import SubwayLine, SubwayStation
from .bus import BusLine
from .spot import ScenicSpot
