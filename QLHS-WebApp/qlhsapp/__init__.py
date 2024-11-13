from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:%s@localhost/qlhsdb?charset=utf8mb4' % quote("tiendatmySQL964@")
db = SQLAlchemy(app=app)