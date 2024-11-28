# DAO chứa các phương thức tương tác xuống CSDL
import random
import string

import unicodedata
from sqlalchemy import func
from flask_mail import Message
from qlhsapp import app, db, mail
from qlhsapp.models import Student, User, Account, Subject, Staff, Teacher
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

def load_subject():
    return Subject.query.all()

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

def add_account(account_id, username, password, role):
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

def add_staff(staff_id):
    s = Staff(staff_id=staff_id)
    db.session.add(s)
    db.session.commit()

def add_teacher(teacher_id, subject_id):
    t = Teacher(teacher_id=teacher_id, subject_id=subject_id)
    db.session.add(t)
    db.session.commit()

def find_user_by_email(email):
    return db.session.query(User).filter_by(email=email).first()

def send_email(user_email, username, password):
    """
    Gửi email chứa thông tin tài khoản đến user.email.
    """
    try:
        # Tạo nội dung email
        msg = Message(
            subject="Thông tin tài khoản của bạn",
            sender=app.config['MAIL_DEFAULT_SENDER'],  # Sử dụng cấu hình mặc định của ứng dụng
            recipients=[user_email]  # Email người nhận
        )
        # Nội dung email
        msg.body = f"""
        Chào bạn,

        Chúc mừng bạn đã đăng ký tài khoản thành công.

        Username: {username}
        Mật khẩu: {password}

        Vui lòng đăng nhập và thay đổi mật khẩu của bạn ngay sau khi đăng nhập.

        Trân trọng,
        Đội ngũ hỗ trợ.
        """
        # Gửi email
        mail.send(msg)
        print(f"Email đã được gửi đến {user_email}")
    except Exception as e:
        print(f"Không thể gửi email: {e}")


def remove_accents(input_str):
    # Loại bỏ dấu tiếng Việt
    nfkd_form = unicodedata.normalize('NFKD', input_str)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])


def generate_username(last_name):
    # Chuyển last_name thành chữ thường và không có dấu
    last_name = remove_accents(last_name.lower())

    # Tạo username = last_name + 6 chữ số ngẫu nhiên
    random_numbers = ''.join(random.choices(string.digits, k=6))
    return f"{last_name}{random_numbers}"

def generate_password():
    # Tạo password ngẫu nhiên gồm chữ cái và số
    characters = string.ascii_letters + string.digits
    password = ''.join(random.choices(characters, k=10))  # Password dài 10 ký tự
    return password

def get_password_by_account_id(account_id):
    account = Account.query.get(account_id)
    if account:
        return account.password  # Trả về mật khẩu đã lưu trong cơ sở dữ liệu
    return None  # Trường hợp không tìm thấy tài khoản

def password_encryption(password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    return password