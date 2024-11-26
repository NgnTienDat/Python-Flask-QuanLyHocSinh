# DAO chứa các phương thức tương tác xuống CSDL
import math

from flask import flash

from qlhsapp import app, db

from qlhsapp.models import ScoreType, Score, Regulation, Student, Class, Teacher, GradeLevel, StudentClass, GenderEnum
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


def handle_add_new_class(name, grade_level_id, homeroom_teacher_id, school_year_id, school_year_name):
    if Class.query.filter_by(name=name, school_year_id=school_year_id).first():
        flash(f'Lớp {name} thuộc năm học {school_year_name} đã tồn tại trong hệ thống!', 'warning')
        return False

    teacher = Teacher.query.filter_by(teacher_id=homeroom_teacher_id).first()
    teacher.is_homeroom_teacher = True
    # tam thoi dung staff_id = 5 -> Sau nay dang nhap dc se sua
    new_class = Class(name=name, grade_level_id=grade_level_id,
                      homeroom_teacher_id=homeroom_teacher_id, school_year_id=school_year_id, staff_id=5,
                      student_numbers=0)
    db.session.add(new_class)
    db.session.commit()
    flash('Thêm mới lớp học thành công!', 'success')
    return True


def filter_class_by_grade_level_id(grade_level_id, page=1):
    page_size = 5
    start = (page - 1) * page_size

    query = Class.query

    if grade_level_id != 'all':
        query = query.filter_by(grade_level_id=int(grade_level_id))

    total_records = query.count()  # Tong so ban ghi
    total_pages = (total_records + page_size - 1) // page_size

    classes = query.offset(start).limit(page_size).all()
    return classes, total_pages


def load_student_no_assigned(kw=None, page=1):
    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size

    query = Student.query.filter_by(in_assigned=False)

    total_records = query.count()  # Tong so ban ghi
    total_pages = math.ceil(total_records / page_size)

    if kw:
        query = query.filter(Student.name.contains(kw))

    students = query.offset(start).limit(page_size).all()
    return students, total_pages


def update_class(class_id, new_homeroom_teacher_id, class_name):
    try:
        class_ = Class.query.get(class_id)

        if class_.name != class_name or class_.homeroom_teacher_id != new_homeroom_teacher_id:
            hr_old = Teacher.query.get(class_.homeroom_teacher_id)
            hr_old.is_homeroom_teacher = False  # cap nhat cho gvcn hien tai thanh false

            hr_new = Teacher.query.get(new_homeroom_teacher_id)
            hr_new.is_homeroom_teacher = True  # cap nhat cho gvcn moi thanh true

            class_.homeroom_teacher_id = new_homeroom_teacher_id
            class_.name = class_name

            db.session.commit()
            flash('Cập nhật lớp học thành công!', 'success')
        return True

    except Exception as e:
        db.session.rollback()
        print(f"ĐÃ xảy ra lỗi: {str(e)}")
        return False


def add_student_to_class(student_list_id, class_id):
    class_ = Class.query.get(class_id)
    class_max_size = Regulation.query.filter_by(key_name='CLASS_MAX_SIZE').first()
    available_slots = int(class_max_size.value) - class_.student_numbers
    if available_slots >= len(student_list_id):
        for student_id in student_list_id:
            student = Student.query.get(student_id)
            if student:
                student_class = StudentClass(student_id=student_id, class_id=class_id, is_active=True)
                class_.student_numbers += 1
                student.in_assigned = True
                db.session.add(student_class)
                db.session.flush()
        db.session.commit()
        flash('Phân lớp thành công!!', 'success')
        return True
    flash('Số học sinh quá sĩ số tối đa!!', 'warning')
    return False


def count_student_un_assigned():
    return Student.query.filter_by(in_assigned=False).count()


def automatic_assign_students_to_class():
    # si so toi da
    class_max_size = Regulation.query.filter_by(key_name='CLASS_MAX_SIZE').first()  #
    # cac lop hoc can them hoc sinh
    classes = Class.query.filter(Class.student_numbers < int(class_max_size.value)).all()
    if not classes:
        flash('Các lớp học đã đạt sĩ số tối đa!!', 'warning')
        return False
    # cac hoc sinh chua phan lop
    students = Student.query.filter_by(in_assigned=False).all()  #
    if not students:
        flash('Không có học sinh!!', 'warning')
        return False
    print(f'chua phan lop: {count_student_un_assigned()}')
    # danh sach hoc sinh nam va nu
    # Lọc học sinh nam và nữ
    male_students = [s for s in students if s.gender == GenderEnum.MALE]
    female_students = [s for s in students if s.gender == GenderEnum.FEMALE]
    print(f'nam: {male_students}')
    print(f'nu: {female_students}')
    # so lop hoc hien tai
    numbers_current_classes = Class.query.count()  # ---
    # so hoc sinh nam va nu
    male_numbers = len(male_students)  # ---
    female_numbers = len(female_students)
    print(f'so hs nam: {male_numbers}')
    print(f'so hs nu: {female_numbers}')

    # so lop hoc toi thieu phai co
    min_numbers_class = math.ceil(count_student_un_assigned() / int(class_max_size.value))  # ---
    print(f'Số lớp tối thiểu: {min_numbers_class}')
    # neu so lop hoc hien tai it hon so lop hoc toi thieu phai co
    if numbers_current_classes < min_numbers_class:
        flash('Phân lớp không thành công!!', 'warning')
        return False
    male_numbers_in_class = male_numbers // min_numbers_class
    print(f'nam 1 lop: {male_numbers_in_class}')
    female_numbers_in_class = female_numbers // min_numbers_class
    print(f'nu 1 lop: {female_numbers_in_class}')
    idx = 0
    for i in range(male_numbers):
        if idx == min_numbers_class:
            break
        curr_class = classes[idx]
        if curr_class.student_numbers < int(class_max_size.value):

            stu_class = StudentClass(student_id=male_students[i].id,
                                     class_id=curr_class.id, is_active=True)
            classes[idx].student_numbers += 1
            male_students[i].in_assigned = True
            db.session.add(stu_class)
            print('for1')
        if (i + 1) % male_numbers_in_class == 0:  # vong lap chay tu 0 -> i = 8 la du 9 nam
            idx += 1


    print('pass for1')
    idx = 0
    for i in range(female_numbers):
        print(f'for 2: {i}')
        if idx == min_numbers_class:
            break

        curr_class = classes[idx]
        if curr_class.student_numbers < int(class_max_size.value):
            print(f'if')
            stu_class = StudentClass(student_id=female_students[i].id,
                                     class_id=curr_class.id, is_active=True)
            classes[idx].student_numbers += 1
            female_students[i].in_assigned = True
            db.session.add(stu_class)
            print('for2')
        if (i + 1) % female_numbers_in_class == 0:
            idx += 1
    # dau : la lay phan con lai
    remaining_male = male_students[male_numbers_in_class*min_numbers_class:] # 11*3=33 lay tu 33 cho den end
    remaining_female = female_students[female_numbers_in_class*min_numbers_class:] # 8*3=24
    print(f'reamain male {len(remaining_male)}')
    print(f'reamain male {len(remaining_female)}')
    remain_student = remaining_male + remaining_female
    idx = 0
    for student in remain_student:
        while classes[idx].student_numbers >= int(class_max_size.value):
            idx+=1
        stu_class = StudentClass(student_id=student.id,
                                 class_id=classes[idx].id, is_active=True)
        classes[idx].student_numbers += 1
        student.in_assigned = True
        db.session.add(stu_class)
        print('for3')


    db.session.commit()
    print('commit')
    flash('Phân lớp thành công!!', 'success')
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

        # luu thong tin xuong csdl
        if db.session.is_modified(student):
            db.session.commit()
            print("Changes committed successfully.")
        else:
            print("No changes detected.")
    except Exception as e:
        db.session.rollback()  # Rollback nếu có lỗi
        print(f"An error occurred: {str(e)}")
        flash(f"An error occurred while updating: {str(e)}", "danger")


# Trung code: Xóa học sinh
def delete_student(student_id):
    student = Student.query.get(student_id)
    if student:
        db.session.delete(student)
        db.session.commit()
    else:
        raise ValueError("Không tìm thấy học sinh cần xóa")


# Trung code: Tiếp nhận học sinh
def add_sutdent():
    pass
