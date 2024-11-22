# DAO chứa các phương thức tương tác xuống CSDL
from flask import flash

from qlhsapp import app, db


from qlhsapp.models import ScoreType, Score, Regulation, Student
from datetime import datetime



def load_score_regulation():
    return ScoreType.query.all()


def check_exist_score_type(score_type):
    existing_score_type = ScoreType.query.filter_by(name=score_type).first()
    return existing_score_type


def handle_add_score_regulation(score_type, score_quantity, coefficient):
    if score_quantity < 1 or score_quantity > 10 or coefficient < 1 or coefficient > 10:
        flash('Hệ số và cột điểm phải trong khoảng từ 1 đến 10', 'warning')
        return False
    if check_exist_score_type(score_type):
        flash('Loại điểm này đã tồn tại!!!', 'danger')
        return False

    new_score_type = ScoreType(name=score_type,
                               score_quantity=score_quantity,
                                coefficient=coefficient)
    db.session.add(new_score_type)
    db.session.commit()
    flash('Thêm loại điểm mới thành công!', 'success')
    return True


def get_score_type_by_name(name):
    return ScoreType.query.filter_by(name=name).first()

def update_score_regulation(score_type, score_quantity, coefficient):
    st = check_exist_score_type(score_type)
    if st:
        st.score_quantity = int(score_quantity)
        st.coefficient = int(coefficient)
        db.session.commit()
        return True

def update_class_size(key_name, value):
    if value > 100 or value < 10:
        flash('Sĩ số phải trong khoảng từ 10 đến 100', 'warning')
        return False
    regulation = Regulation.query.filter_by(key_name=key_name).first()
    if regulation:
        regulation.value = value
        db.session.commit()
        flash('Cập nhật sĩ số tối đa thành công!', 'success')
        return True


def update_age_regulation(min_age, max_age):
    if min_age >= max_age:
        flash('Số tuổi tối thiểu phải nhỏ hơn số tuổi tối đa!!', 'warning')
        return False
    max_age_reg = Regulation.query.filter_by(key_name='MAX_AGE').first()
    min_age_reg = Regulation.query.filter_by(key_name='MIN_AGE').first()

    if min_age_reg and max_age_reg:
        min_age_reg.value = min_age
        max_age_reg.value = max_age
        db.session.commit()
        flash('Cập nhật số tuổi thành công!', 'success')
        return True

def load_student(kw=None, page=1):
    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size

    students = Student.query.offset(start).limit(page_size).all()

    if kw:
        students = [s for s in students if s.name.lower().find(kw.lower()) >= 0]

    return students


def get_student_by_id(student_id):
    return Student.query.get(student_id)


def count_student():
    return Student.query.count()


# Trung code: cập nhật thông tin học sinh
def update_student(student_id, name, address, email, date_of_birth, phone_number):
    student = Student.query.get(student_id)  # Lấy học sinh muốn cập nhật
    # Chuyển đổi ngày sinh từ chuỗi sang date trước khi lưu xuống database
    date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d").date()

    try:
        # Cập nhật thông tin học sinh
        student.name = name
        student.address = address
        student.email = email
        student.date_of_birth = date_of_birth
        student.phone_number = phone_number

        #luu thong tin xuong csdl
        if db.session.is_modified(student):
            db.session.commit()
            print("Changes committed successfully.")
        else:
            print("No changes detected.")
    except Exception as e:
        db.session.rollback()  # Rollback nếu có lỗi
        print(f"An error occurred: {str(e)}")
        flash(f"An error occurred while updating: {str(e)}", "danger")


#Trung code: Xóa học sinh
def delete_student(student_id):
    student = Student.query.get(student_id)
    if student:
        db.session.delete(student)
        db.session.commit()
    else:
        raise ValueError("Không tìm thấy học sinh cần xóa")


#Trung code: Tiếp nhận học sinh
def add_sutdent():
    pass