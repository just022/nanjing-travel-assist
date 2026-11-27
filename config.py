# config.py
import os

class Config:
    DEBUG = True
    SECRET_KEY = "nanjing-travel-2026-bys"
    # 改成你自己mysql账号密码！
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:Root1234@localhost:3306/nanjing_travel"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
