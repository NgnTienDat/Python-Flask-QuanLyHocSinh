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
                            SchoolYear, Semester, GradeLevel, Account, Staff, TeachingAssignment)


from flask import request

from datetime import datetime



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
    password = str(hashlib.md5(password.encode('utf-8')).hexdigest())
    return Account.query.filter(Account.username.__eq__(username.strip()),
                                Account.password.__eq__(password)).first()


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
        student.in_assigned=False
        class_.student_numbers-=1
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
            subject_id=subject_id,school_year_id=school_year_id).first()

        print(teacher_id)
        print(exist_ta.teacher_id)
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
                        subject_id=subject_id,school_year_id=school_year_id).first()
    if ta:
        return ta.teacher_id
    return 0




def load_student(kw=None, page=1):#chưa phân trang
    page_size = app.config['PAGE_SIZE']
    start = (page - 1) * page_size

    students = Student.query.offset(start).limit(page_size).all()

    if kw:
        students = [s for s in students if s.name.lower().find(kw.lower()) >= 0]

    return students


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


def get_all_class():
    return Class.query.all()


def get_semester(school_year_id):
    semesters = Semester.query.filter(Semester.school_year_id == school_year_id).all()
    return semesters


def load_score_columns():
    return ScoreType.query.all()


def get_students_by_class(class_id):
    students = StudentClass.query.filter_by(class_id=class_id).all()
    return students
