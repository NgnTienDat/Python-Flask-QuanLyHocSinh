# DAO chứa các phương thức tương tác xuống CSDL
from sqlalchemy import func

from qlhsapp import app, db
from qlhsapp.models import Student, User, Account
import hashlib
import cloudinary.uploader
from flask import request

# def load_score_regulation():
#     return ScoreRegulation.query.all()

def load_users(kw=None):
    page = request.args.get('page', 1, type=int)
    query = User.query
    page_size = app.config['PAGE_SIZE']
    # Nếu `kw` không trống, lọc theo từ khóa trong tên nhân viên
    if kw:
        query = query.filter(User.first_name.contains(kw) | User.last_name.contains(kw) | User.email.contains(kw) | Student.phone_number.contains(kw))

    return query.paginate(page=page, per_page=page_size)

def delete_user_from_db(user_id):
    user = User.query.get(user_id)
    if user:
        db.session.delete(user)
        db.session.commit()
    else:
        raise ValueError("Không tìm thấy người dùng cần xóa")

def delete_account_from_db(user_id):
    account = Account.query.get(user_id)
    if account:
        db.session.delete(account)
        db.session.commit()
    else:
        raise ValueError("Không tìm thấy tài khoản cần xóa")

def find_user(id):
    return User.query.get(id)

def auth_account(username, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    return Account.query.filter(Account.username.__eq__(username.strip()),
                             Account.password.__eq__(password)).first()

def add_account(account_id,username,password,role):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    a = Account(account_id=account_id, username=username, password=password, role=role)
    db.session.add(a)
    db.session.commit()

def get_account_by_id(account_id):
    return Account.query.get(account_id)

def add_user(first_name, last_name, address, email, phone_number, avatar=None):
    # Kiểm tra email đã tồn tại
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        raise ValueError("Email này đã được sử dụng")

    u = User(first_name=first_name, last_name=last_name, address=address, email=email,
             phone_number=phone_number)

    if avatar:
        try:
            res = cloudinary.uploader.upload(avatar)
            u.avatar = res.get('secure_url')  # Lấy URL của ảnh đã upload
        except Exception as e:
            raise ValueError(f"Lỗi khi upload avatar: {e}")
    db.session.add(u)
    db.session.commit()
    return u.id

def find_user_by_email(email):
    return db.session.query(User).filter_by(email=email).first()

