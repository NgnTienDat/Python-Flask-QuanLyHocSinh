# DAO chứa các phương thức tương tác xuống CSDL
from sqlalchemy import func

from qlhsapp import app, db
from qlhsapp.models import Student, User, Account
from flask import request
from sqlalchemy.sql import text
import hashlib


# def load_score_regulation():
#     return ScoreRegulation.query.all()


def load_students(kw=None):
    page = request.args.get('page', 1, type=int)
    query = Student.query
    page_size = app.config['PAGE_SIZE']
    # Nếu `kw` không trống, lọc theo từ khóa trong tên nhân viên
    if kw:
        query = query.filter(Student.name.contains(kw) | Student.email.contains(kw) | Student.phone_number.contains(kw))

    return query.paginate(page=page, per_page=page_size)


def delete_student_from_db(student_id):
    """
    Xóa sinh viên khỏi database theo ID.

    :param student_id: ID của sinh viên cần xóa
    """
    try:
        sql = text("DELETE FROM student WHERE id = :id")
        db.session.execute(sql, {"id": student_id})
        db.session.commit()
        print(f"Đã xóa sinh viên có ID {student_id} thành công.")
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi xóa sinh viên có ID {student_id}: {e}")

def find_student(id):
    return Student.query.get(id)

def load_users(kw=None):
    page = request.args.get('page', 1, type=int)
    query = User.query
    page_size = app.config['PAGE_SIZE']
    # Nếu `kw` không trống, lọc theo từ khóa trong tên nhân viên
    if kw:
        query = query.filter(User.first_name.contains(kw) | User.last_name.contains(kw) | User.email.contains(kw) | Student.phone_number.contains(kw))

    return query.paginate(page=page, per_page=page_size)


def delete_user_from_db(user_id):
    """
    Xóa người dùng khỏi database theo ID.

    :param user_id: ID của người dùng cần xóa
    """
    try:
        sql = text("DELETE FROM user WHERE id = :id")
        db.session.execute(sql, {"id": user_id})
        db.session.commit()
        print(f"Đã xóa người dùng có ID {user_id} thành công.")
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi khi xóa người dùng có ID {user_id}: {e}")

def find_user(id):
    return User.query.get(id)

def auth_account(username, password):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    return Account.query.filter(Account.username.__eq__(username.strip()),
                             Account.password.__eq__(password)).first()

def add_account(account_id,username,password,role):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    u = Account(account_id=account_id, username=username, password=password, role=role)
    db.session.add(u)
    db.session.commit()

def get_account_by_id(account_id):
    return Account.query.get(account_id)


