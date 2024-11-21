# DAO chứa các phương thức tương tác xuống CSDL
from qlhsapp import app, db
from qlhsapp.models import ScoreRegulation, Student
from flask import request
import sqlite3

def load_score_regulation():
    return ScoreRegulation.query.all()

def load_students(kw=None):
    page = request.args.get('page', 1, type=int)
    query = Student.query
    page_size = app.config['PAGE_SIZE']
    # Nếu `kw` không trống, lọc theo từ khóa trong tên nhân viên
    if kw:
        query = query.filter(Student.name.contains(kw) | Student.email.contains(kw) | Student.phone_number.contains(kw))

    return query.paginate(page=page, per_page=page_size)

def delete_student_from_db(id):
    connection = sqlite3.connect('D:/PycharmProject/Python-Flask-QuanLyHocSinh/QLHS-WebApp/qlhsapp/data/database.db')
    cursor = connection.cursor()
    cursor.execute("DELETE FROM student WHERE id = ?", (id,))
    connection.commit()
    connection.close()

def get_db_connection():
    conn = sqlite3.connect('./data/database.db')
    conn.row_factory = sqlite3.Row
    return conn