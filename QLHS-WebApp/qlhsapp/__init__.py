from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import cloudinary

app = Flask(__name__)

app.secret_key = '^&*)%T*O&T*^&%)*^T%*&T)*O&RTO)(*#@$%@#$%*@FSK'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:tiendatmySQL964%40@localhost/qlhsdb?charset=utf8mb4'



db = SQLAlchemy(app=app)

cloudinary.config(
    cloud_name = 'dleseuevb',
    api_key = '482437994953727',
    api_secret = '6Xtl72oMfsJ6luFsm77ho6LnciU'
)