from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:1234@localhost/qlhsdb?charset=utf8mb4"
app.secret_key = '^&*)%T*O&T*^&%)*^T%*&T)*O&RTO)(*@#$%@#THIPQ#asf'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:tiendatmySQL964%40@localhost/qlhsdb?charset=utf8mb4'

app.config['PAGE_SIZE'] = 8


db = SQLAlchemy(app=app)
