from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
from sqlalchemy import create_engine
import cloudinary
from flask_login import LoginManager
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = "WTFTHANGNGUPHANLENGUYEN"

# Cấu hình cơ sở dữ liệu
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:%s@localhost/database?charset=utf8mb4" % quote('Admin@123')

# Cấu hình mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Gmail SMTP server
app.config['MAIL_PORT'] = 587  # Sử dụng TLS
app.config['MAIL_USE_TLS'] = True  # Bật TLS
app.config['MAIL_USERNAME'] = 'qkhanh1632@gmail.com'  # Thay bằng email của bạn
app.config['MAIL_PASSWORD'] = 'eeqm sumi hxgj egsn'  # Thay bằng mật khẩu ứng dụng của bạn
app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@gmail.com'  # Email gửi mặc định

# Các cấu hình khác
app.config["PAGE_SIZE"] = 8
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], echo=True, future=True)

# Cấu hình Cloudinary
cloudinary.config(
    cloud_name='dabb0yavq',
    api_key='629417998313995',
    api_secret='Pz7QaOBFl3nGzZVfWWmb2Vvx3DQ',
    secure=True
)

# Khởi tạo các đối tượng
db = SQLAlchemy(app)
login_manager = LoginManager(app)
mail = Mail(app)
