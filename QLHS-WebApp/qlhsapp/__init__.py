from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
app = Flask(__name__)

# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:1234@localhost/qlhsdb?charset=utf8mb4"
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:tiendatmySQL964%40@localhost/qlhsdb?charset=utf8mb4'

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'data/database.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 8


db = SQLAlchemy(app=app)
