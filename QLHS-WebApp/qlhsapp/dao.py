# DAO chứa các phương thức tương tác xuống CSDL
from flask import flash

from qlhsapp import app, db

from qlhsapp.models import (ScoreType, Score, Regulation, Student,
                            GenderEnum, Class, Teacher, Subject, StudentClass, User,
                            Account, UserRole, SchoolYear, Semester)
from datetime import datetime
import re


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


def handle_add_new_class(name, grade_level_id, homeroom_teacher_id, school_year_id, school_year_name):
    if Class.query.filter_by(name=name, school_year_id=school_year_id).first():
        flash(f'Lớp {name} thuộc năm học {school_year_name} đã tồn tại trong hệ thống!', 'warning')
        return False

    teacher = Teacher.query.filter_by(teacher_id=homeroom_teacher_id).first()
    teacher.is_homeroom_teacher = True

    new_class = Class(name=name, grade_level_id=grade_level_id,
                      homeroom_teacher_id=homeroom_teacher_id, school_year_id=school_year_id)
    db.session.add(new_class)
    db.session.commit()
    flash('Thêm mới lớp học thành công!', 'success')
    return True


def get_student_by_id(student_id):
    return (db.session.query(Student.id,
                             Student.name,
                             Student.address,
                             Student.email,
                             Student.gender,
                             Student.date_of_birth,
                             Student.phone_number,
                             Class.name.label("current_class"))
            .join(StudentClass, StudentClass.student_id == Student.id)
            .join(Class, StudentClass.class_id == Class.id)
            .filter(Student.id == student_id)
            .first()
            )


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

        # luu thong tin xuong csdl
        if db.session.is_modified(student):
            db.session.commit()
            print("Changes committed successfully.")
        else:
            print("No changes detected.")
    except Exception as e:
        db.session.rollback()  # Rollback nếu có lỗi
        print(f"An error occurred: {str(e)}")
        flash(f"Lỗi update: {str(e)}", "danger")


# Trung code: Xóa học sinh
def delete_student(student_id):
    student = Student.query.get(student_id)
    if student:
        db.session.delete(student)
        db.session.commit()
    else:
        raise ValueError("Không tìm thấy học sinh cần xóa")


# Trung code: Tiếp nhận học sinh
def add_student(name, address, gender, date_of_birth, staff_id, **kwargs):
    gender = GenderEnum(gender)
    date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d").date()
    try:
        student = Student(name=name,
                          address=address,
                          gender=gender,
                          date_of_birth=date_of_birth,
                          staff_id=staff_id,
                          email=kwargs.get('email'),
                          phone_number=kwargs.get('phone_number'))
        db.session.add(student)
        db.session.commit()
    except ValueError as ve:
        db.session.rollback()
        print(f"Lỗi thêm giới tính: {gender}. Error: {ve}")
    except Exception as e:
        db.session.rollback()
        print(f"Lỗi thêm học sinh: {e}")


def check_email_student(current_email):
    existing_student = Student.query.filter_by(email=current_email).first()
    return existing_student is not None  # cần check lại chỗ này !!!!!


def validate_input(name, address, phone_number, email):
    if len(name) < 3 or len(name) > 50:
        flash("Tên học sinh phải có độ dài từ 3 đến 50 ký tự.", "warning")
        return False
    if email and len(email) > 50:
        flash("email phải ít hơn 50 ký tự.", "warning")
        return False
    if len(address) < 3 or len(address) > 50:
        flash("Địa chỉ phải có độ dài từ 3 đến 50 ký tự.", "warning")
        return False
    if phone_number and len(phone_number) != 10:
        flash("Số điện thoại phải có đúng 10 chữ số", "warning")
        return False
    return True


def load_subject():
    subjects = Subject.query.all()
    return subjects


def save_subject(name):
    subject = Subject(name=name)
    db.session.add(subject)
    db.session.commit()


def handel_save_subject(name):
    existing_subject = Subject.query.filter_by(name=name).first()
    return existing_subject is not None


def get_subject_by_id(subject_id):
    return Subject.query.get(subject_id)


def delete_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if subject:
        db.session.delete(subject)
        db.session.commit()
    else:
        raise ValueError("Không tìm thấy môn học cần xóa")


def list_students(kw=None):
    students = (
        db.session.query(Student.id,
                         Student.name,
                         Student.address,
                         Student.email,
                         Student.gender,
                         Student.date_of_birth,
                         Student.phone_number,
                         Class.name.label("current_class"))
        .join(StudentClass, StudentClass.student_id == Student.id)
        .join(Class, StudentClass.class_id == Class.id)
        .filter(StudentClass.is_active == True)
        .all()
    )

    if kw:
        students = [s for s in students if s.name.lower().find(kw.lower()) >= 0]

    return students


def get_teacher_by_id(teacher_id):
    return Teacher.query.filter(Teacher.teacher_id == teacher_id).first()


def update_teacher(teacher_id, last_name, first_name, email, address, phone_number, avatar):
    teacher = User.query.get(teacher_id)
    try:
        teacher.last_name = last_name
        teacher.first_name = first_name
        teacher.email = email
        teacher.address = address
        teacher.phone_number = phone_number
        teacher.avatar = avatar

        # Kiểm tra nếu có thay đổi trong session
        if db.session.is_modified(teacher):
            db.session.commit()
            print("Changes committed successfully.")
        else:
            print("No changes detected.")
    except Exception as e:
        db.session.rollback()  # Rollback nếu có lỗi
        print(f"An error occurred: {str(e)}")
        flash(f"Lỗi cập nhật: {str(e)}", "danger")


def delete_teacher(teacher_id):
    teacher = User.query.get(teacher_id)
    if teacher:
        db.session.delete(teacher)
        db.session.commit()
    else:
        raise ValueError("Không tìm thấy giáo viên cần xóa")


def get_current_school_year():
    return SchoolYear.query.order_by(SchoolYear.id.desc()).first()


def get_all_class():
    return Class.query.all()


def get_semester(school_year_id):
    semesters = Semester.query.filter(Semester.school_year_id == school_year_id).all()
    return semesters


def load_score_columns():
    return ScoreType.query.all()


