# app.py
from flask import Flask
from config import Config
from models import db
from routes import main_bp, subway_bp, bus_bp, route_bp, spot_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # 初始化数据库
    db.init_app(app)

    # 注册蓝图
    app.register_blueprint(main_bp)
    app.register_blueprint(subway_bp)
    app.register_blueprint(bus_bp)
    app.register_blueprint(route_bp)
    app.register_blueprint(spot_bp)

    return app


app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
