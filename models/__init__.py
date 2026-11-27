# models/__init__.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

from .subway import SubwayLine, SubwayStation
from .bus import BusLine, BusStation
from .spot import ScenicSpot
from .city import City
from .user import User, RouteFavorite
