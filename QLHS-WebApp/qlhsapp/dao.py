# DAO chứa các phương thức tương tác xuống CSDL

import random
import string
import math
import hashlib
import cloudinary.uploader

import unicodedata
from flask import flash
from sqlalchemy import func
from flask_mail import Message
from qlhsapp import app, db, mail

from qlhsapp.models import Student, User, Account, Subject, Staff, Teacher
import hashlib
import cloudinary.uploader

from qlhsapp.models import (ScoreType, Score, Regulation, Student,
                            GenderEnum, Class, Teacher, Subject, StudentClass, User,
                            SchoolYear, Semester, GradeLevel, Account, Staff, TeachingAssignment, ScoreBoard)

from flask import request

from datetime import datetime


def load_list_users(kw=None, page=1):
    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size

    query = User.query.join(Account).filter(Account.active == True)

    print(query)
    total_records = query.count()  # Tong so ban ghi
    total_pages = math.ceil(total_records / page_size)

    if kw:
        query = query.filter(User.first_name.contains(kw) | User.last_name.contains(kw) | User.email.contains(kw))

    users = query.offset(start).limit(page_size).all()
    return users, total_pages


def update_subject(subject_id, name):
    subject = Subject.query.get(subject_id)
    if subject:
        subject.name = name
        db.session.commit()
        flash('Cập nhật thành công!', 'success')
        return True
    flash('Cập nhật không thành công!', 'danger')
    return False


def load_users(kw=None):
    page = request.args.get('page', 1, type=int)
    query = User.query
    page_size = app.config['PAGE_SIZE']
    # Nếu `kw` không trống, lọc theo từ khóa trong tên nhân viên
    if kw:
        query = query.filter(User.first_name.contains(kw) | User.last_name.contains(kw) | User.email.contains(
            kw) | Student.phone_number.contains(kw))

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
    is_active = False
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    account =  Account.query.filter(Account.username.__eq__(username.strip()),
                                Account.password.__eq__(password)).first()
    if account and account.active == 1:
        is_active = True
    return account, is_active


def add_account(account_id, username, password, role):
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    a = Account(account_id=account_id,
                username=username,
                password=password,
                role=role)
    db.session.add(a)
    db.session.commit()


def get_account_by_id(account_id):
    return Account.query.get(account_id)


def add_user(first_name, last_name, address, email, phone_number, avatar=None):
    # Kiểm tra email đã tồn tại
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        raise ValueError("Email này đã được sử dụng")

    u = User(first_name=first_name,
             last_name=last_name,
             address=address,
             email=email,
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
            subject="Hệ thống quản lý học sinh - Thông tin tài khoản của bạn",
            sender=app.config['MAIL_DEFAULT_SENDER'],
            recipients=[user_email]  # Email người nhận
        )
        msg.body = f"""
        Chào bạn,

        Chúng tôi xin gửi đến bạn thông tin tài khoản. Vui lòng sử dụng thông tin dưới đây để đăng nhập:
        
        Thông tin tài khoản:
        Username: {username}
        Mật khẩu: {password}

        Vì lý do bảo mật, vui lòng thay đổi mật khẩu của bạn sau lần đăng nhập đầu tiên.
        Không chia sẻ thông tin tài khoản với bất kỳ ai để đảm bảo an toàn.

        Trân trọng,
        Hệ thống quản lý học sinh.
        """
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
                      homeroom_teacher_id=homeroom_teacher_id, school_year_id=school_year_id, staff_id=2,
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


def load_student_in_assigned(selected_class_id, page=1, kw=None):
    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size

    query = StudentClass.query.filter_by(class_id=selected_class_id, is_active=True)

    total_records = query.count()  # Tong so ban ghi
    total_pages = math.ceil(total_records / page_size)

    if kw:
        query = query.filter(Student.name.contains(kw))

    student_class = query.offset(start).limit(page_size).all()
    return student_class, total_pages


def handle_remove_student_from_class(student_id):
    student_from_class = StudentClass.query.filter_by(student_id=student_id, is_active=True).first()
    student = Student.query.get(student_id)
    class_ = Class.query.get(student_from_class.class_id)

    if student_from_class and student and class_:
        db.session.delete(student_from_class)
        student.in_assigned = False
        class_.student_numbers -= 1
        db.session.commit()
        return True, class_.id
    return False


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


def add_new_school_year(year1, year2, start_hk1, finish_hk1, start_hk2, finish_hk2):
    if len(year1) == 4 and len(year2) == 4 and int(year2) == int(year1) + 1:
        start_hk1 = datetime.strptime(start_hk1, "%Y-%m-%d")
        finish_hk1 = datetime.strptime(finish_hk1, "%Y-%m-%d")
        start_hk2 = datetime.strptime(start_hk2, "%Y-%m-%d")
        finish_hk2 = datetime.strptime(finish_hk2, "%Y-%m-%d")

        sy = f'{year1}-{year2}'
        school_year = SchoolYear(name=sy)
        db.session.add(school_year)
        db.session.flush()

        hk1 = Semester(start_date=start_hk1, finish_date=finish_hk1, name='HK1', school_year_id=school_year.id)
        hk2 = Semester(start_date=start_hk2, finish_date=finish_hk2, name='HK2', school_year_id=school_year.id)
        db.session.add_all([hk1, hk2])
        db.session.commit()

        flash('Tạo năm học mới thành công!', 'success')
        return True

    flash('Năm học phải đủ 4 chữ số và cách nhau 1 năm!', 'danger')
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


# phan lop tu dong theo so HS/Lop
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
        flash('Phân lớp không thành công do không đủ lớp học. Tạo thêm lớp học hoặc nâng sĩ số tối đa lên!', 'warning')
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
    remaining_male = male_students[male_numbers_in_class * min_numbers_class:]  # 11*3=33 lay tu 33 cho den end
    remaining_female = female_students[female_numbers_in_class * min_numbers_class:]  # 8*3=24
    print(f'reamain male {len(remaining_male)}')
    print(f'reamain male {len(remaining_female)}')
    remain_student = remaining_male + remaining_female
    idx = 0
    for student in remain_student:
        while classes[idx].student_numbers >= int(class_max_size.value):
            idx += 1
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


def add_teaching_assignment(teacher_id, class_id, subject_id, school_year_id):
    try:
        exist_ta = TeachingAssignment.query.filter_by(class_id=class_id,
                                                      subject_id=subject_id, school_year_id=school_year_id).first()

        if exist_ta and exist_ta.teacher_id == teacher_id:
            flash(f'Bản phân công này đã tồn tại!!', 'danger')
            return False
        if exist_ta and exist_ta.teacher_id != teacher_id:
            exist_ta.teacher_id = teacher_id
            db.session.commit()
            flash(f'Cập nhật phân công mới thành công!!', 'success')
            return True

        ta = TeachingAssignment(teacher_id=teacher_id, class_id=class_id, subject_id=subject_id,
                                school_year_id=school_year_id)
        db.session.add(ta)
        db.session.commit()
        flash(f'Lưu thành công!!', 'success')
        return True
    except Exception as e:
        db.session.rollback()
        flash(f'Đã xảy ra sự cố trong quá trình lưu: {e}', 'danger')
        return False


def get_teacher_id_assigned(subject_id, class_id, school_year_id):
    ta = TeachingAssignment.query.filter_by(class_id=class_id,
                                            subject_id=subject_id, school_year_id=school_year_id).first()
    if ta:
        return ta.teacher_id
    return 0


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


def count_teacher():
    return Teacher.query.count()


def count_subject():
    return Subject.query.count()


def count_class():
    return Class.query.count()


# Trung code: cập nhật thông tin học sinh
def update_student(student_id, name, address, email, date_of_birth, phone_number):
    student = Student.query.get(student_id)  # Lấy học sinh muốn cập nhật
    date_of_birth = datetime.strptime(date_of_birth, "%Y-%m-%d").date()

    try:
        student.name = name
        student.address = address
        student.email = email
        student.date_of_birth = date_of_birth
        student.phone_number = phone_number

        if db.session.is_modified(student):
            db.session.commit()
            flash('Cập nhật học sinh thành công!', 'success')
            print("Changes committed successfully.")
        else:
            print("No changes detected.")
    except Exception as e:
        db.session.rollback()  # Rollback nếu có lỗi
        print(f"An error occurred: {str(e)}")
        flash(f"Lỗi update: {str(e)}", "danger")


def get_school_years_with_semesters():
    query = (
        db.session.query(
            SchoolYear.id,
            SchoolYear.name,
            Semester.name,
            Semester.start_date,
            Semester.finish_date
        )
        .join(Semester, SchoolYear.id == Semester.school_year_id)
    )
    results = query.all()
    return results


def format_school_year_data(results):
    school_years = {}
    for school_year_id, school_year_name, semester_name, start_date, finish_date in results:
        if school_year_id not in school_years:
            school_years[school_year_id] = {
                "name": school_year_name,
                "semesters": {}
            }
        school_years[school_year_id]["semesters"][semester_name] = {
            "start_date": start_date,
            "finish_date": finish_date
        }
    return school_years


# Trung code: Xóa học sinh
def delete_student(student_id):
    student_from_class = StudentClass.query.filter_by(student_id=student_id, is_active=True).first()
    class_ = Class.query.get(student_from_class.class_id)
    student = Student.query.get(student_id)

    if student_from_class and student and class_:
        db.session.delete(student)
        class_.student_numbers -= 1
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
        flash("Tên phải có độ dài từ 3 đến 50 ký tự.", "warning")
        return False
    if email and len(email) > 50:
        flash("Email phải ít hơn 50 ký tự.", "warning")
        return False
    if len(address) < 3 or len(address) > 50:
        flash("Địa chỉ phải có độ dài từ 3 đến 50 ký tự.", "warning")
        return False
    if phone_number and len(phone_number) != 10:
        flash("Số điện thoại phải có đúng 10 chữ số", "warning")
        return False
    return True


def load_subject(kw=None):
    subjects = Subject.query.all()
    if kw:
        subjects = Subject.query.filter(Subject.name.contains(kw))
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

def get_all_subject():
    return Subject.query.all()


def delete_subject(subject_id):
    teaching_assignments = TeachingAssignment.query.filter_by(subject_id=subject_id).all()
    # chua the xoa mon hoc neu trong qua khu co giao vien day mon hoc do du hien tai mon hoc khong con duoc day
    if teaching_assignments:
        return False
    subject = Subject.query.get(subject_id)
    if subject:
        db.session.delete(subject)
        db.session.commit()

        return True
    flash("Không tìm thấy môn học", "danger")
    return False


def load_teachers(kw=None, page=1):
    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size
    query = (db.session.query(Teacher, User)
             .join(Teacher, User.id == Teacher.teacher_id)
             .filter(User.account.has(active=True))  # Điều kiện kiểm tra active=True
             )
    total_records = query.count()
    total_pages = math.ceil(total_records / page_size)
    if kw:
        query = query.filter(User.first_name.ilike(f"%{kw}%") | User.last_name.ilike(f"%{kw}%"))
    results = query.offset(start).limit(page_size).all()
    return results, total_pages


def list_students(kw=None, class_id=None, page=1):
    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size

    query = (
        db.session.query(StudentClass, Student, Class)
        .join(Student, StudentClass.student_id == Student.id)
        .join(Class, StudentClass.class_id == Class.id)
        .filter(StudentClass.is_active == True)
    )

    total_records = query.count()
    total_pages = math.ceil(total_records / page_size)

    if kw:
        query = query.filter(Student.name.ilike(f"%{kw}%"))  # Sử dụng ilike để không phân biệt chữ hoa/chữ thường

    if class_id:
        query = query.filter(Class.id == class_id)

    results = query.offset(start).limit(page_size).all()
    print(results)
    return results, total_pages


def get_teacher_by_id(teacher_id):
    return Teacher.query.filter(Teacher.teacher_id == teacher_id).first()


def update_teacher(teacher_id, last_name, first_name, email, address, phone_number, avatar, subject_id):
    teacher = User.query.get(teacher_id)
    try:
        teacher.last_name = last_name
        teacher.first_name = first_name
        teacher.email = email
        teacher.address = address
        teacher.phone_number = phone_number
        teacher.avatar = avatar
        teacher.teacher.subject_id = subject_id

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

def get_all_school_year():
    return SchoolYear.query.all()


def get_all_class():
    return Class.query.all()


def get_semester(school_year_id):
    semesters = Semester.query.filter(Semester.school_year_id == school_year_id).all()
    return semesters


def load_score_columns():
    return ScoreType.query.all()


def get_students_by_class(class_id):
    students = (
        StudentClass.query
        .filter_by(class_id=class_id)
        .join(Student, StudentClass.student_id == Student.id)
        .filter(StudentClass.student_id != None)
        .all()
    )
    return students


def calculate_average_score(score_columns, score_data, student_id):
    total_score = 0
    total_coefficient = 0
    for col in score_columns:
        for i in range(col.score_quantity):
            score_key = f"score_{student_id}_{col.id}_{i + 1}"
            score_value = score_data.get(score_key)

            if score_value:
                total_score += float(score_value) * col.coefficient
                total_coefficient += col.coefficient

    return total_score / total_coefficient if total_coefficient > 0 else 0


def save_score(student_id, subject_id, teacher_id, semester_id, score_columns, score_data):
    score_board = db.session.query(ScoreBoard).filter_by(
        student_id=student_id,
        subject_id=subject_id,
        teacher_id=teacher_id,
        semester_id=semester_id
    ).first()

    if not score_board:
        score_board = ScoreBoard(
            student_id=student_id,
            subject_id=subject_id,
            teacher_id=teacher_id,
            semester_id=semester_id
        )
        db.session.add(score_board)
        db.session.commit()

    # Lấy các điểm đã lưu hiện tại theo scoretype và index để cập nhật neeus có cập nhật
    existing_scores = {}
    for score in score_board.scores:
        existing_scores[(score.score_type, score.index)] = score

    for col in score_columns:
        for i in range(col.score_quantity):
            score_key = f"score_{student_id}_{col.id}_{i + 1}"
            score_value = score_data.get(score_key)

            if score_value is not None:
                score_value = float(score_value)

                if (col.id, i) in existing_scores:  # nếu có loại điểm và chỉ số cần cập nhật thì cập nhật lại điểm mới
                    existing_scores[(col.id, i)].score_value = score_value
                else:
                    new_score = Score(
                        score_type=col.id,
                        index=i,
                        score_value=score_value,
                        score_board_id=score_board.id
                    )
                    db.session.add(new_score)

    average_score = calculate_average_score(score_columns, score_data, student_id)
    score_board.average_score = average_score
    db.session.commit()


def get_score_boards(subject_id, semester_id):
    score_boards = db.session.query(ScoreBoard).filter_by(subject_id=subject_id,
                                                          semester_id=semester_id).all()
    return score_boards


def extract_score_data(student, score_columns, form_data):
    score_data = {}
    for col in score_columns:
        for i in range(col.score_quantity):
            score_value = form_data.get(f"score_{student.student_id}_{col.id}_{i + 1}")
            if score_value:
                score_data[f"score_{student.student_id}_{col.id}_{i + 1}"] = float(score_value)
    return score_data


def prepare_scores(subject_id, semester_id):
    scores = {}
    if semester_id and subject_id:
        score_boards = get_score_boards(subject_id, semester_id)  # lấy hết bảng điểm của môn học X ở học kỳ Y
        for score_board in score_boards:
            student_id = score_board.student_id
            scores[student_id] = {
                'average_score': score_board.average_score  # Điểm trung bình
            }
            for score in score_board.scores:  # lấy từng điêmr trong danh sách điểm của một hsinh
                scores[student_id].setdefault(score.score_type, []).append(score.score_value)
    return scores


def get_class_teacher(teacher_id):
    current_school_year = get_current_school_year()

    if teacher_id == 1:
        # Khi teacher_id là 1, lấy tất cả các lớp trong cơ sở dữ liệu cho học kỳ hiện tại
        class_teacher = TeachingAssignment.query.filter_by(school_year_id=current_school_year.id).all()
    else:
        # Khi teacher_id khác 1, chỉ lấy các lớp mà giáo viên đó dạy trong học kỳ hiện tại
        class_teacher = TeachingAssignment.query.filter_by(teacher_id=teacher_id,
                                                           school_year_id=current_school_year.id).all()

    return class_teacher


def get_class_by_id(class_id):
    class_info = Class.query.filter_by(id=class_id).first()  # Lọc theo class_id để lấy thông tin lớp
    return class_info


def get_teacher_classes_details(teacher_id, semester_id, subject_id,class_id=None):
    # Lấy các lớp mà giáo viên dạy
    class_teacher = get_class_teacher(teacher_id)
    class_ids = [assignment.class_id for assignment in class_teacher]  # Lấy danh sách các class_id

    # Lấy thông tin chi tiết của từng lớp
    class_details = []

    # Nếu có class_id, chỉ lấy thông tin lớp đó
    if class_id:
        class_info = get_class_by_id(class_id)
        passed_students = get_passed_students(class_info.id, semester_id, subject_id)
        rate = get_pass_rate(class_info.id, semester_id, subject_id)

        class_details.append({
            'id': class_info.id,  # Trả về id lớp
            'name': class_info.name,  # Trả về tên lớp
            'student_numbers': class_info.student_numbers,  # Trả về số học sinh
            'passed_students': passed_students,  # Trả về số học sinh đạt
            'rate': rate  # Trả về tỷ lệ phần trăm học sinh đạt
        })
    else:
        # Nếu không có class_id, lấy tất cả các lớp mà giáo viên dạy
        for cls_id in class_ids:
            class_info = get_class_by_id(cls_id)

            # Lấy số học sinh đạt của lớp cho môn học và học kỳ
            passed_students = get_passed_students(class_info.id, semester_id, subject_id)
            rate = get_pass_rate(class_info.id, semester_id ,subject_id)

            # Thêm thông tin lớp vào danh sách
            class_details.append({
                'id': class_info.id,  # Trả về id lớp
                'name': class_info.name,  # Trả về tên lớp
                'student_numbers': class_info.student_numbers,  # Trả về số học sinh
                'passed_students': passed_students,  # Trả về số học sinh đạt
                'rate': rate  # Trả về tỷ lệ phần trăm học sinh đạt
            })

    return class_details


def get_passed_students(class_id, semester_id, subject_id):
    """
    Trả về số lượng học sinh đạt của một lớp trong một học kỳ cho một môn học cụ thể.
    :param class_id: ID của lớp học.
    :param semester_id: ID của học kỳ.
    :param subject_id: ID của môn học.
    :return: Số lượng học sinh đạt.
    """
    passed_students = db.session.query(func.count(ScoreBoard.student_id)) \
        .join(StudentClass, StudentClass.student_id == ScoreBoard.student_id) \
        .filter(
            StudentClass.class_id == class_id,
            ScoreBoard.average_score >= 5,
            ScoreBoard.semester_id == semester_id,  # Lọc theo học kỳ
            ScoreBoard.subject_id == subject_id     # Lọc theo môn học
        ) \
        .scalar()

    return passed_students


def get_pass_rate(class_id, semester_id, subject_id):
    """
    Tính tỷ lệ phần trăm học sinh đậu trong một lớp học.

    Args:
        class_id (int): ID của lớp học.

    Returns:
        float: Tỷ lệ học sinh đậu (từ 0 đến 100).
    """
    # Lấy tổng số học sinh trong lớp
    total_students = db.session.query(func.count(Student.id)) \
        .join(StudentClass, Student.id == StudentClass.student_id) \
        .filter(StudentClass.class_id == class_id) \
        .scalar()

    # Lấy tổng số học sinh đã đậu
    passed_students = get_passed_students(class_id, semester_id, subject_id)

    # Nếu không có học sinh nào trong lớp, trả về tỷ lệ đậu là 0
    if total_students == 0:
        return 0.0

    # Tính tỷ lệ đậu (làm tròn 2 chữ số thập phân)
    pass_rate = (passed_students / total_students) * 100
    return round(pass_rate, 2)


def get_class_by_homeroom_teacher_id(id):
    return Class.query.filter_by(homeroom_teacher_id=id).first()


def calculate_student_average(student_id, class_id, semester_id):
    # Kiểm tra học sinh có thuộc lớp hay không
    is_student_in_class = db.session.query(StudentClass).filter_by(
        class_id=class_id, student_id=student_id
    ).first()
    if not is_student_in_class:
        return 0.0  # Nếu học sinh không thuộc lớp, trả về 0

    # Lấy danh sách môn học
    teaching_assignments = load_subject()

    total_score = 0
    total_coefficient = 0

    # Duyệt qua tất cả các môn học
    for assignment in teaching_assignments:
        subject_id = assignment.id

        # Lấy bảng điểm của học sinh cho môn học này trong học kỳ
        score_board = db.session.query(ScoreBoard).filter_by(
            student_id=student_id,
            subject_id=subject_id,
            semester_id=semester_id
        ).first()

        # Nếu có điểm trung bình cho môn học, cộng vào tổng điểm
        if score_board and score_board.average_score is not None:
            total_score += score_board.average_score  # Cộng điểm trung bình môn học
            total_coefficient += 1  # Tăng hệ số cho môn học này

    # Tính điểm trung bình
    if total_coefficient > 0:
        return round(total_score / total_coefficient, 2)
    else:
        return 0.0



def get_student_ids_by_class_id(class_id, semester_id):
    """
    Lấy danh sách thông tin chi tiết (student_id, name, gender, điểm trung bình, học lực) của học sinh
    dựa vào class_id và semester_id.

    Args:
        class_id (int): ID của lớp học.
        semester_id (int): ID của học kỳ.

    Returns:
        List[Dict]: Danh sách các thông tin của học sinh thuộc class_id và semester_id.
    """
    # Tham gia bảng `StudentClass` với bảng `Student` để lấy thông tin chi tiết
    student_classes = (
        db.session.query(
            StudentClass.student_id,
            Student.name,
            Student.gender
        )
        .join(Student, StudentClass.student_id == Student.id)
        .filter(StudentClass.class_id == class_id)
        .all()
    )

    # Kết hợp thông tin chi tiết, tính điểm trung bình và phân loại học lực
    students_with_averages = []
    for student in student_classes:
        student_id = student.student_id
        name = student.name
        gender = student.gender.value  # Lấy giá trị của Enum
        if gender == "MALE":
            gender = "Nam"
        elif gender == "FEMALE":
            gender = "Nữ"

        # Tính điểm trung bình cho học sinh trong học kỳ tương ứng
        average_score = calculate_student_average(student_id, class_id, semester_id)

        # Phân loại học lực
        if average_score < 5:
            grade = "Yếu"
        elif 5 <= average_score < 6.5:
            grade = "Trung Bình"
        elif 6.5 <= average_score < 8:
            grade = "Khá"
        elif 8 <= average_score <= 10:
            grade = "Giỏi"
        else:
            grade = "Không xác định"

        students_with_averages.append({
            "student_id": student_id,
            "name": name,
            "gender": gender,
            "average_score": average_score,
            "grade": grade
        })

    return students_with_averages
