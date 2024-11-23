from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
from sqlalchemy import create_engine
import cloudinary
from flask_login import LoginManager
app = Flask(__name__)
app.secret_key = "WTFTHANGNGUPHANLENGUYEN"
# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:1234@localhost/qlhsdb?charset=utf8mb4"
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:tiendatmySQL964%40@localhost/qlhsdb?charset=utf8mb4'
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/database?charset=utf8mb4" % quote('Admin@123')

# basedir = os.path.abspath(os.path.dirname(__file__))
# app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(basedir, 'data/database.db')}"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["PAGE_SIZE"] = 8
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], echo=True, future=True)
cloudinary.config(
    cloud_name='dabb0yavq',
    api_key='629417998313995',
    api_secret='Pz7QaOBFl3nGzZVfWWmb2Vvx3DQ',
    secure=True
)
db = SQLAlchemy(app)
login_manager = LoginManager(app)

