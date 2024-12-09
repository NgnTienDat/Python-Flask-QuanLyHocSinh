from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from urllib.parse import quote
from sqlalchemy import create_engine
import cloudinary
from flask_login import LoginManager
from flask_mail import Mail, Message


app = Flask(__name__)



app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@localhost/qlhsdb?charset=utf8mb4'


# Cấu hình mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Gmail SMTP server
app.config['MAIL_PORT'] = 587  # Sử dụng TLS
app.config['MAIL_USE_TLS'] = True  # Bật TLS
app.config['MAIL_USERNAME'] = 'qkhanh1632@gmail.com'
app.config['MAIL_PASSWORD'] = 'eeqm sumi hxgj egsn'
app.config['MAIL_DEFAULT_SENDER'] = 'no-reply@gmail.com'  # Email gửi mặc định

# Các cấu hình khác
app.secret_key = '^&*)%T*O&T*^&%)*^T%*&T)*O&RTO)(*@#$%@#THIPQ#asf'
app.config["PAGE_SIZE"] = 8
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"], echo=True, future=True)

# Cấu hình Cloudinary
cloudinary.config(
    cloud_name='derx1izam',
    api_key='826692895649512',
    api_secret='aEf9hn_PrTeOXTOOJCz6k8Ucf3U',
    secure=True
)
# Khởi tạo các đối tượng
db = SQLAlchemy(app=app)
login_manager = LoginManager(app)
mail = Mail(app)

# Cấu hình LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login_process'
login_manager.login_message = ""

