from flask import render_template, request, redirect, url_for, flash, make_response
from qlhsapp import app, db, login_manager
import dao
from flask_login import login_user, logout_user, login_required, current_user
import math

from qlhsapp.models import (ScoreType, Score, Regulation, Student,
                            Teacher, GradeLevel, SchoolYear, Class, StudentClass, Subject, TeachingAssignment, Semester,
                            Account)

import cloudinary.uploader


@app.route("/")
@login_required
def get_home_page():
    quantity_student = dao.count_student()
    quantity_teacher = dao.count_teacher()
    quantity_subject = dao.count_subject()
    quantity_class = dao.count_class()
    return render_template('admin/index.html',
                           quantity_class=quantity_class,
                           quantity_student=quantity_student,
                           quantity_subject=quantity_subject,
                           quantity_teacher=quantity_teacher)


@login_manager.user_loader
def get_user_by_id(user_id):
    return dao.get_account_by_id(user_id)


@app.route("/login", methods=['GET', 'POST'])
def login_process():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        print(username)
        print(password)

        # Xác thực tài khoản
        user, is_active = dao.auth_account(username=username, password=password)
        if user and is_active:
            login_user(user)
            # Kiểm tra vai trò
            print(user.role)
            if user.role.value == 'ADMIN':
                # Chuyển hướng tới trang Flask-Admin
                print('admin here')
                return redirect('/admin')

            # Chuyển hướng tới trang chính
            return redirect(url_for('get_home_page'))
        elif user and not is_active:
            flash('Tài khoản bị ngừng hoạt động!', 'danger')
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'danger')

    return render_template('login.html')


# Trung code: Tra cuu hoc sinh
@app.route("/students")
def find_student_page():
    page = request.args.get('page', 1)
    kw = request.args.get("key-name")
    class_id = request.args.get("class_id")
    classes = dao.get_all_class()

    stu_class, pages = dao.list_students(kw=kw, class_id=class_id, page=int(page))
    if not stu_class:
        flash(f'Không có học sinh nào tên {kw}.', 'warning')

    account = db.session.get(Account, current_user.account_id)
    r = account.role
    if r.value == 'STAFF':
        return render_template('staff/find-student.html',
                               students=stu_class, pages=pages, page=int(page), classes=classes,
                               selected_class=class_id)
    elif r.value == 'TEACHER':
        return render_template('teacher/find-student.html',
                               students=stu_class, pages=pages, page=int(page), classes=classes,
                               selected_class=class_id)
    return render_template('admin/find-student.html',
                           students=stu_class, pages=pages, page=int(page), classes=classes, selected_class=class_id)


@app.route("/logout")
def logout_process():
    logout_user()
    return redirect(url_for('login_process'))


# Tiếp nhận học sinh
@app.route("/add-student", methods=['get', 'post'])
def add_student_page():
    if request.method.__eq__('POST'):
        try:
            name = request.form.get('name')
            address = request.form.get('address')
            email = request.form.get('email')
            gender = request.form.get('gender')
            date_of_birth = request.form.get('date_of_birth')
            phone_number = request.form.get('phone_number')
            staff_id = current_user.account_id
            print(f"Received data: name={name}, address={address}, email={email}, "
                  f"gender={gender}, date_of_birth={date_of_birth}, phone_number={phone_number}")
            # kiểm tra tính hợp lệ của thông tin nhập vào
            # Gọi hàm validate từ dao
            if not dao.validate_input(name, address, phone_number, email, date_of_birth):
                return redirect(url_for('add_student_page'))
            if dao.check_email_student(email):
                flash("Email đã tồn tại !!!", "warning")
                return redirect(url_for('add_student_page'))
            print(staff_id)
            dao.add_student(name=name, address=address, gender=gender, date_of_birth=date_of_birth, staff_id=staff_id,
                            email=email,
                            phone_number=phone_number)

            flash("Thêm học sinh thành công!", "success")
        except Exception as ex:
            print(f"Error occurred: {ex}")
            flash(f"Đã xảy ra lỗi khi thêm học sinh: {ex}", "error")

    return render_template('admin/add-student.html')


# Phân lớp học sinh
@app.route("/set-class", methods=['get', 'post'])
def set_class_page():
    page = request.args.get('page', 1)
    if request.method == 'POST':

        action = request.form.get('action')

        if action == 'automatic':
            try:

                if dao.automatic_assign_students_to_class():
                    return redirect(url_for('set_class_page'))

            except Exception as e:
                flash(f'Lỗi xảy ra trong quá trình phân lớp: {str(e)}', 'danger')
                return redirect(url_for('set_class_page'))

        else:
            try:
                # lay gia tri cua cac checkbox gui len duoi dang list
                selected_students = request.form.getlist('student_id')
                class_id = int(request.form.get('class_'))
                print(selected_students)
                print(class_id)
                if dao.add_student_to_class(student_list_id=selected_students, class_id=class_id):
                    return redirect(url_for('set_class_page'))


            except (TypeError, ValueError):
                flash('Bạn chưa chọn lớp học hoặc chọn học sinh!!', 'warning')
                return redirect(url_for('set_class_page'))

    total_unassigned_students = dao.count_student_un_assigned()
    classes = Class.query.all()

    selected_class_id = request.args.get('class_sel_id', type=int, default=0)
    if selected_class_id != 0:
        # Nếu đã chọn lớp, lấy danh sách học sinh của lớp đó
        student_class, pages = dao.load_student_in_assigned(selected_class_id, page=int(page))
        students = [sc.students for sc in student_class]
    else:
        students, pages = dao.load_student_no_assigned(page=int(page))

    return render_template('staff/set-class.html',
                           classes=classes, students=students, pages=pages, page=int(page),
                           total_unassigned_students=total_unassigned_students,
                           selected_class_id=selected_class_id)


@app.route("/set-class/remove/<int:student_id>", methods=['get', 'post'])
def remove_student_from_class(student_id):
    print(student_id)
    status, class_id = dao.handle_remove_student_from_class(student_id)
    if status:
        flash('Xóa thành công!', 'success')
        return redirect(url_for('set_class_page', class_sel_id=class_id))
    else:
        flash('Loại điểm không tồn tại!', 'danger')
        return redirect(url_for('set_class_page'))


@app.route('/school-year')
def school_year_page():
    school_years = SchoolYear.query.order_by(SchoolYear.id.desc()).all()
    semesters = Semester.query.order_by(Semester.id.desc()).all()
    school_years_semesters = dao.get_school_years_with_semesters()
    results = dao.format_school_year_data(school_years_semesters)
    account = db.session.get(Account, current_user.account_id)
    r = account.role
    if r.value == 'ADMIN':
        return render_template('admin/school-year.html', school_years=results)

    return render_template('staff/school-year.html', school_years=results)


@app.route('/school-year/new-school-year', methods=['get', 'post'])
def add_new_school_year():
    if request.method == 'POST':
        try:
            year1 = request.form.get('school_year1')
            year2 = request.form.get('school_year2')
            start_hk1 = request.form.get('start_hk1')
            finish_hk1 = request.form.get('finish_hk1')
            start_hk2 = request.form.get('start_hk2')
            finish_hk2 = request.form.get('finish_hk2')

            if dao.add_new_school_year(year1, year2, start_hk1, finish_hk1, start_hk2, finish_hk2):
                return redirect(url_for('school_year_page'))


        except (TypeError, ValueError):
            flash('Dữ liệu không hợp lệ!!', 'warning')
            return redirect(url_for('school_year_page'))

    return render_template('admin/new-school-year.html')


# Quy định số cột điểm
@app.route("/score-regulation", methods=['get', 'post'])
def score_regulations_page():
    if request.method.__eq__('POST'):
        scores_update = []
        try:
            # chia nguyen de lay so dong, vi du 9 o input thi 9//3=3 dong, lap tung dong
            for index in range(1, len(request.form) // 3 + 1):
                score_type = request.form.get(f'score_type_{index}')
                score_quantity = int(request.form.get(f'score_quantity_{index}'))
                coefficient = int(request.form.get(f'coefficient_{index}'))

                scores_update.append({
                    'score_type': score_type,
                    'score_quantity': score_quantity,
                    'coefficient': coefficient
                })
                print(scores_update)
        except (TypeError, ValueError):
            flash('Dữ liệu không hợp lệ, vui lòng nhập số nguyên!!', 'warning')
            return redirect(url_for('score_regulations_page'))

        for data in scores_update:
            score_type = data['score_type']  # chỉ gửi lên chuỗi ví dụ '15 phút'
            score_quantity = data['score_quantity']
            coefficient = data['coefficient']

            dao.update_score_regulation(score_type, score_quantity, coefficient)

        flash('Cập nhật thay đổi thành công!', 'success')
        return redirect(url_for('score_regulations_page'))

    score_types = dao.load_score_regulation()
    account = db.session.get(Account, current_user.account_id)
    r = account.role
    if r.value == 'ADMIN':
        return render_template('admin/score.html', score_types=score_types)

    return render_template('staff/score.html', score_types=score_types)


@app.route("/add-new-score-type", methods=['get', 'post'])
def new_score_regulation():
    if request.method == 'POST':
        try:
            score_type = request.form.get('score_type')
            score_quantity = int(request.form.get('score_quantity'))
            coefficient = int(request.form.get('coefficient'))
        except (ValueError, TypeError):
            flash('Dữ liệu không hợp lệ, vui lòng nhập số nguyên!!', 'warning')
            return render_template('admin/new-score-regulation.html')

        if dao.handle_add_score_regulation(score_type, score_quantity, coefficient):
            return redirect(url_for('score_regulations_page'))

    return render_template('admin/new-score-regulation.html')


@app.route('/score-regulation/<int:score_type_id>', methods=['get', 'post'])
def delete_score_type(score_type_id):
    score = ScoreType.query.get(score_type_id)
    if request.method == 'POST':

        score = ScoreType.query.get(score_type_id)

        if score:
            db.session.delete(score)
            db.session.commit()
            flash('Xóa thành công!', 'success')
        else:
            flash('Loại điểm không tồn tại!', 'danger')
        return redirect(url_for('score_regulations_page'))

    return render_template('admin/delete-score-type.html', score=score)


# Quy định số học sinh
@app.route("/numbers-regulation", methods=['get', 'post'])
def numbers_regulations_page():
    if request.method == 'POST':
        try:
            class_max_size = int(request.form.get('class_max_size'))
        except (ValueError, TypeError):
            flash('Dữ liệu không hợp lệ, vui lòng nhập số nguyên!!', 'warning')
            return redirect(url_for('numbers_regulations_page'))

        if dao.update_class_size(key_name='CLASS_MAX_SIZE', value=class_max_size):
            return redirect(url_for('numbers_regulations_page'))

    class_size = Regulation.query.filter_by(key_name='CLASS_MAX_SIZE').first()
    account = db.session.get(Account, current_user.account_id)
    r = account.role
    if r.value == 'ADMIN':
        return render_template('admin/numbers.html', class_size=class_size)
    return render_template('staff/numbers.html', class_size=class_size)


# Quy định tuổi
@app.route("/age-regulation", methods=['get', 'post'])
def age_regulations_page():
    if request.method == 'POST':
        print(request.form.get('max_age'))
        print(request.form.get('min_age'))
        try:
            max_age = int(request.form.get('max_age'))
            min_age = int(request.form.get('min_age'))
        except (ValueError, TypeError):
            flash('Dữ liệu không hợp lệ, vui lòng nhập số nguyên!!', 'warning')
            return redirect(url_for('age_regulations_page'))

        if dao.update_age_regulation(min_age=min_age, max_age=max_age):
            return redirect(url_for('age_regulations_page'))

    max_age = Regulation.query.filter_by(key_name='MAX_AGE').first()
    min_age = Regulation.query.filter_by(key_name='MIN_AGE').first()

    account = db.session.get(Account, current_user.account_id)
    r = account.role
    if r.value == 'ADMIN':
        return render_template('admin/age.html', max_age=max_age, min_age=min_age)
    return render_template('staff/age.html', max_age=max_age, min_age=min_age)


@app.route("/list-teacher/teaching-assignment", methods=['get', 'post'])
def teaching_assignment():
    if request.method == 'POST':
        try:
            subject_id = request.form.get('subject')
            class_id = request.form.get('class_')
            school_year_id = request.form.get('school_year_id')
            teacher_id = request.form.get('teacher')
            print(subject_id)
            print(class_id)
            print(school_year_id)
            print(teacher_id)
            if dao.add_teaching_assignment(teacher_id=teacher_id, class_id=class_id,
                                           subject_id=subject_id, school_year_id=school_year_id):
                # giu nguyen trang thai mon hoc da chon subject_filter=subject_id
                return redirect(url_for('teaching_assignment', subject_filter=subject_id,
                                        class_filter=class_id))
        except Exception as e:
            flash(f"Đã xảy ra lỗi trong quá trình lưu: {str(e)}", "danger")
            return redirect(url_for('teaching_assignment', subject_filter=request.form.get('subject'),
                                    class_filter=request.form.get('class_')))

    subjects = Subject.query.all()
    classes = Class.query.all()
    school_year = SchoolYear.query.order_by(SchoolYear.id.desc()).first()

    default_class = Class.query.filter_by(school_year_id=school_year.id).first()
    subject_id = request.args.get('subject_filter')
    class_id = request.args.get('class_filter')
    selected_subject = subject_id
    selected_class = class_id
    teachers = Teacher.query.filter_by(subject_id=subject_id).all()

    t_assignment_id = dao.get_teacher_id_assigned(class_id=class_id,
                                                  subject_id=subject_id, school_year_id=school_year.id)

    return render_template('admin/teaching-assignment.html', subjects=subjects,
                           classes=classes, school_year=school_year, selected_subject=selected_subject,
                           selected_class=selected_class, teachers=teachers, teacher_is_assigned=t_assignment_id)


# Nhập điểm
@app.route("/input-score", methods=['get', 'post'])
def input_score():
    class_id = request.args.get('class_id') or request.form.get('class_id')
    semester_id = request.args.get('semester_id') or request.form.get('semester_id')
    subject_id = request.args.get('subject_id') or request.form.get('subject_id')

    current_year = dao.get_current_school_year()
    if current_year is None:
        print("No current school year found!")
        # Xử lý trường hợp không có năm học hiện tại, ví dụ:
        return "Error: No current school year available"
    classes = dao.get_class_teacher(current_user.user.id)
    semesters = dao.get_semester(current_year.id) if current_year else []
    score_columns = dao.load_score_columns()
    students = dao.get_students_by_class(class_id)
    scores = dao.prepare_scores(subject_id, semester_id)

    if request.method == 'POST':
        if not semester_id or not class_id:
            flash(f"Lỗi lưu điểm: Chưa chọn lớp hoặc học kỳ", "danger")
        else:
            teacher_id = request.form.get('teacher_id')
            for student in students:
                student_id = student.student_id
                score_data = dao.extract_score_data(student, score_columns,
                                                    request.form)  # lấy các cột điểm của hs từ form về dạng từ điểm để lưu
                dao.save_score(student_id, subject_id, teacher_id, semester_id, score_columns, score_data)
            scores = dao.prepare_scores(subject_id, semester_id)  # load lại điểm lúc nhấn lưu

    return render_template(
        'teacher/input-score.html',
        current_year=current_year,
        classes=classes,
        semesters=semesters,
        score_columns=score_columns,
        students=students,
        selected_class_filter=class_id,
        scores=scores,
        selected_semester_filter=semester_id
    )


# Xuất điểm
@app.route("/export-score")
def export_score():
    class_id = request.args.get('class_id') or request.form.get('class_id')
    semester_id = request.args.get('semester_id') or request.form.get('semester_id')
    subject_id = request.args.get('subject_id') or request.form.get('subject_id')
    export_format = request.args.get('export')  # Kiểm tra nếu xuất Excel

    current_year = dao.get_current_school_year()
    classes = dao.get_class_teacher(current_user.user.id)
    semesters = dao.get_semester(current_year.id) if current_year else []
    score_columns = dao.load_score_columns()
    students = dao.get_students_by_class(class_id)

    # lay diem hien len giao dien
    if semester_id == "all_semester":
        scores = dao.get_all_average_scores(subject_id, class_id, current_year.id)
    else:
        scores = dao.prepare_scores(subject_id, semester_id)

    if export_format == "excel":
        # Gọi hàm tạo file Excel
        return dao.export_to_excel(semester_id, scores, students)
    return render_template('teacher/export-score.html',
                           current_year=current_year,
                           classes=classes,
                           semesters=semesters,
                           score_columns=score_columns,
                           students=students,
                           selected_class_filter=class_id,
                           scores=scores,
                           selected_semester_filter=semester_id)


@app.route("/list-teacher")
def list_teacher():
    page = request.args.get('page', 1)
    kw = request.args.get('kw')
    teachers, pages = dao.load_teachers(kw=kw, page=int(page))

    account = db.session.get(Account, current_user.account_id)
    r = account.role
    if r.value == 'ADMIN':
        return render_template('admin/teacher.html', teachers=teachers, pages=pages, page=int(page))
    return render_template('staff/teacher.html', teachers=teachers, pages=pages, page=int(page))


@app.route("/list-teacher/<int:teacher_id>")
def teacher_detail(teacher_id):
    teacher = dao.get_teacher_by_id(teacher_id)
    return render_template('admin/teacher-detail.html', teacher=teacher)


@app.route("/list-teacher//update/<int:teacher_id>", methods=['get', 'post'])
def teacher_update(teacher_id):
    teacher = dao.get_teacher_by_id(teacher_id)
    subjects = dao.load_subject()
    if request.method.__eq__('POST'):
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        email = request.form.get('email')
        address = request.form.get('address')
        phone_number = request.form.get('phone_number')
        avatar_path = teacher.user.avatar
        avatar = request.files.get('avatar')
        subject_id = request.form.get('subject_id')
        if avatar and avatar.filename != '':
            try:
                res = cloudinary.uploader.upload(avatar)
                avatar_path = res['secure_url']
            except Exception as e:
                print(f"Avatar upload error: {str(e)}")
                flash(f"Lỗi tải ảnh: {str(e)}", "danger")
        print(subject_id)
        dao.update_teacher(teacher_id=teacher_id,
                           last_name=last_name,
                           first_name=first_name,
                           email=email,
                           address=address,
                           phone_number=phone_number,
                           avatar=avatar_path,
                           subject_id=subject_id)
        return redirect(url_for('list_teacher'))
    return render_template('admin/update-teacher.html', teacher=teacher, subjects=subjects)


@app.route("/list-teacher//delete/<int:teacher_id>", methods=['get', 'post'])
def delete_teacher(teacher_id):
    teacher = dao.get_teacher_by_id(teacher_id)
    if request.method.__eq__('POST'):
        try:
            dao.delete_user_from_db(teacher_id)
            return redirect(url_for('list_teacher'))
        except Exception as e:
            flash(f"Lỗi: {str(e)}", "danger")
            return redirect(url_for('list_teacher'))
    return render_template('admin/delete-teacher.html', teacher=teacher)


@app.route("/list-subject")
def list_subject():
    kw = request.args.get("key-name")
    subjects = dao.load_subject(kw=kw)

    account = db.session.get(Account, current_user.account_id)
    r = account.role
    if r.value == 'ADMIN':
        return render_template('admin/subject.html', subjects=subjects)
    return render_template('staff/subject.html', subjects=subjects)


@app.route("/list-subject/delete-subject/<int:subject_id>", methods=['get', 'post'])
def delete_subject(subject_id):
    if request.method.__eq__('POST'):
        try:
            if dao.delete_subject(subject_id):
                flash("Xóa môn học thành công.", "success")
            else:
                flash("Không thể xóa môn học vì đang có giáo viên giảng dạy.", "danger")
            return redirect(url_for('list_subject'))
        except Exception as e:
            flash(f"Lỗi: {str(e)}", "danger")
            return redirect(url_for('list_subject'))

    subject = dao.get_subject_by_id(subject_id)
    return render_template('admin/delete-subject.html', subject=subject)


@app.route("/update-subject/<int:subject_id>", methods=['get', 'post'])
def update_subject(subject_id):
    subject = Subject.query.get(subject_id)
    if request.method == 'POST':

        try:
            name = request.form.get('subject_name')
            if dao.update_subject(subject_id, name):
                return redirect(url_for('list_subject'))
        except Exception as e:
            flash(f"Lỗi: {str(e)}", "danger")
            return redirect(url_for('list_subject'))

    return render_template('admin/update-subject.html', subject=subject)


@app.route("/list-class")
def list_class():
    page = request.args.get('page', 1)
    grade_level_id = request.args.get('filter', 'all')  # mac dinh la lay tat ca

    classes, pages = dao.filter_class_by_grade_level_id(grade_level_id, page=int(page))

    grade_levels = GradeLevel.query.all()
    selected_filter = grade_level_id
    return render_template('staff/class.html', classes=classes,
                           grade_levels=grade_levels, selected_filter=selected_filter, pages=pages, page=int(page))


@app.route("/list-class/new-class", methods=['get', 'post'])
def add_new_class():
    if request.method == 'POST':
        class_name = request.form.get('class_name')
        grade_level_id = int(request.form.get('grade_level'))
        homeroom_teacher_id = int(request.form.get('homeroom_teacher'))
        school_year = request.form.get('school_year')
        school_year_id = int(request.form.get('school_year_id'))

        print(type(grade_level_id))
        print(type(homeroom_teacher_id))
        print(type(school_year_id))

        if dao.handle_add_new_class(class_name, grade_level_id, homeroom_teacher_id, school_year_id, school_year):
            return redirect(url_for('add_new_class'))

    teachers = Teacher.query.filter_by(is_homeroom_teacher=False).all()
    print(teachers)
    grade_level = GradeLevel.query.all()
    school_year = SchoolYear.query.order_by(SchoolYear.id.desc()).first()

    return render_template('admin/add-class.html',
                           teachers=teachers, grade_level=grade_level, school_year=school_year)


@app.route("/list-class/update-class/<int:class_id>", methods=['get', 'post'])
def update_class(class_id):
    class_ = Class.query.get(class_id)
    if request.method == 'POST':
        class_name = request.form.get('class_name')
        homeroom_teacher_id = int(request.form.get('homeroom_teacher'))

        if dao.update_class(class_id, homeroom_teacher_id, class_name):
            return redirect(url_for('update_class', class_id=class_id))

    homeroom_teacher_id = class_.homeroom_teacher_id
    school_year = SchoolYear.query.order_by(SchoolYear.id.desc()).first()
    teachers = Teacher.query.filter_by(is_homeroom_teacher=False).all()
    return render_template('admin/update-class.html',
                           school_year=school_year, class_=class_, teachers=teachers,
                           homeroom_teacher_id=homeroom_teacher_id)


# @app.route("/list-user")
# def list_user():
#     page = request.args.get('page', 1)
#     kw = request.args.get('kw')
#     users, pages = dao.load_list_users(kw=kw, page=int(page))
#
#     account = db.session.get(Account, current_user.account_id)
#     r = account.role
#
#     return render_template('admin/list-user.html', users=users, pages=pages)

@app.route("/list-user")
def list_user():
    page = request.args.get('page', 1)
    kw = request.args.get('kw')
    users, pages = dao.load_list_users(kw=kw, page=int(page))

    account = db.session.get(Account, current_user.account_id)
    r = account.role
    if r.value == 'ADMIN':
        return render_template('admin/list-user.html', users=users, pages=pages)
    return render_template('staff/list-user.html', users=users, pages=pages)


@app.route("/delete-user/<int:id>", methods=['DELETE'])
def delete_user(id):
    print(id)
    try:
        a = dao.get_account_by_id(id)
        a.active = False
        db.session.add(a)
        db.session.commit()
        print("Xóa thành công")
        return {"message": "Xóa thành công"}
    except Exception as e:
        print("Xóa thất bại", e)
        return {"message": "Xóa thất bại", "error": str(e)}


# Route để cập nhật thông tin khách hàng
@app.route('/update-user/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    err_msg = ''
    user = dao.find_user(id)  # Lấy thông tin người dùng theo ID

    if request.method == 'POST':
        # Lấy dữ liệu từ form
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        email = request.form['email']
        phone_number = request.form['phone_number']
        status = request.form.get('status')

        # Kiểm tra xem email có bị trùng với người dùng khác không
        existing_user = dao.find_user_by_email(email)
        if existing_user and existing_user.id != id:  # Kiểm tra email trùng với người khác
            err_msg = "Email này đã có người dùng! Vui lòng nhập lại."
        else:
            # Cập nhật thông tin người dùng
            user.first_name = first_name
            user.last_name = last_name
            user.address = address
            user.email = email
            user.phone_number = phone_number
            account = Account.query.get(user.id)
            if account:
                account.active = int(status)

            try:
                # Lưu thay đổi vào database
                db.session.commit()
                return redirect(url_for('list_user'))  # Chuyển hướng về trang chủ
            except Exception as e:
                db.session.rollback()
                err_msg = "Đã xảy ra lỗi trong quá trình cập nhật."

    # Truyền thông tin người dùng vào template để hiển thị
    return render_template('admin/update-user.html', user=user, err_msg=err_msg)


@app.route("/add-user", methods=['GET', 'POST'])
def add_user_page():
    err_msg = ''
    subjects = dao.load_subject()  # Lấy danh sách môn học từ database
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        email = request.form['email']
        phone_number = request.form['phone_number']
        role = request.form['user_role']
        subject_id = request.form.get('subject')  # Lấy subject_id từ form (nếu có)

        # Kiểm tra xem email có tồn tại trong bảng User hoặc Account hay không
        existing_user = dao.find_user_by_email(email)
        if existing_user:
            err_msg = "Email này đã có người dùng! Vui lòng nhập lại."
            return render_template('admin/add-user.html', err_msg=err_msg)

        try:
            # Thêm user vào bảng User
            user_id = dao.add_user(first_name=first_name, last_name=last_name, address=address, email=email,
                                   phone_number=phone_number, avatar=request.files.get('avatar'))

            # Tạo username và password
            username = dao.generate_username(last_name)
            password = dao.generate_password()

            # Thêm tài khoản vào bảng Account
            dao.add_account(account_id=user_id, username=username, password=password, role=role)
            # Thêm Staff hoặc Teacher vào database
            if role == 'STAFF':
                dao.add_staff(user_id)  # Thêm nhân viên
            elif role == 'TEACHER':
                dao.add_teacher(user_id, subject_id)  # Thêm giáo viên với môn học

            # Gửi thông tin tài khoản về email
            dao.send_email(email, username, password)

            # Chuyển hướng sau khi thành công
            return redirect(url_for('add_user_page'))
        except Exception as e:
            err_msg = f"Đã có lỗi xảy ra: {e}"

    return render_template('admin/add-user.html', err_msg=err_msg, subjects=subjects)


@app.route('/change-password/<int:id>', methods=['GET', 'POST'])
def change_password(id):
    account = dao.get_account_by_id(id)
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        current = dao.password_encryption(current_password)
        new = dao.password_encryption(new_password)

        # Kiểm tra tính hợp lệ
        if not current_password or not new_password or not confirm_password:
            return render_template('admin/change_password.html', account=account,
                                   err_msg="Vui lòng nhập đầy đủ thông tin!")

        if new_password != confirm_password:
            return render_template('admin/change_password.html', account=account, err_msg="Mật khẩu mới không khớp!")

        # Giả lập kiểm tra mật khẩu hiện tại (dùng database trong thực tế)
        if current != account.password:  # Thay bằng mật khẩu hiện tại của user từ DB
            return render_template('admin/change_password.html', account=account,
                                   err_msg="Mật khẩu hiện tại không đúng!")

        account.password = new
        try:
            db.session.commit()
            return render_template('admin/change_password.html', account=account,
                                   success_msg="Mật khẩu đã được cập nhật thành công!")
        except Exception as ex:
            db.session.rollback()
            return render_template('admin/change_password.html', account=account,
                                   err_msg="Có lỗi xảy ra, vui lòng thử lại sau!")

    return render_template('admin/change_password.html', account=account)


@app.route("/subject-summary-score")
def subject_summary_score():
    # Role = STAFF
    if current_user.role.value == "STAFF":
        flash("Bạn không có quyền truy cập báo cáo thống kê.", "warning")
        return redirect(url_for('get_home_page'))

    grade_id = request.args.get('grade_id') or request.form.get('grade_id')
    semester_id = request.args.get('semester_id') or request.form.get('semester_id')
    subject_id = request.args.get('subject_id') or request.form.get('subject_id')
    school_year_id = request.args.get('school_year_id') or request.form.get('school_year_id')
    role = current_user.role.value

    if grade_id == 'all':
        grade_id = None

    # Role = ADMIN
    if current_user.role.value == "ADMIN":
        grade_levels = dao.get_all_grade_level()
        classes = dao.get_class_by_grade_level(grade_id)
        subjects = dao.get_all_subject()
        school_years = dao.get_all_school_year()  # Danh sách các niên khóa
        current_year = school_years[0] if school_years else None  # Lấy niên khóa đầu tiên hoặc để None
        if school_year_id:
            semesters = dao.get_semester(school_year_id) if current_year else []
        else:
            semesters = dao.get_semester(current_year.id) if current_year else []
    else:  # Role = TEACHER
        temp = dao.get_class_teacher(current_user.user.id)
        classes = []  # Tạo danh sách rỗng để chứa thông tin lớp học
        for t in temp:
            class_info = dao.get_class_by_id(t.class_id)  # Lấy thông tin lớp dựa vào class_id
            if class_info:  # Kiểm tra nếu class_info không rỗng
                classes.append(class_info)  # Thêm thông tin lớp vào danh sách

        subjects = []
        school_years = []
        grade_levels = []
        current_year = dao.get_current_school_year()
        semesters = dao.get_semester(current_year.id) if current_year else []

    teacher_classes = dao.get_teacher_classes_details(current_user.user.id, semester_id, subject_id, role, grade_id)

    return render_template('admin/subject-summary.html', grade_id=grade_id, semester_id=semester_id,
                           subject_id=subject_id, school_year_id=school_year_id, current_year=current_year,
                           classes=classes, semesters=semesters, grade_levels=grade_levels,
                           teacher_classes=teacher_classes, subjects=subjects, school_years=school_years, role=role)


@app.route("/class-summary-score")
def class_summary_score():
    if current_user.role.value == "STAFF":
        flash("Bạn không có quyền truy cập báo cáo thống kê.", "warning")
        return redirect(url_for('get_home_page'))

    semester_id = request.args.get('semester_id') or request.form.get('semester_id')
    school_year_id = request.args.get('school_year_id') or request.form.get('school_year_id')
    class_id = request.args.get('class_id') or request.form.get('class_id')

    # Chuyển semester_id sang kiểu int, nếu là chuỗi và có thể chuyển đổi được
    if semester_id and semester_id != 'all':
        try:
            semester_id = int(semester_id)
        except ValueError:
            semester_id = None

    # Role = ADMIN
    if current_user.role.value == "ADMIN":
        classes = dao.get_all_class()
        class_name = classes[0] if classes else None
        if class_id and class_id != 'all':
            students = dao.get_student_ids_by_class_id(int(class_id), semester_id)
        else:
            students = dao.get_student_ids_by_class_id(class_name.id, semester_id)

        school_years = dao.get_all_school_year()  # Danh sách các niên khóa
        current_year = school_years[0] if school_years else None  # Lấy niên khóa đầu tiên hoặc để None
        if school_year_id:
            semesters = dao.get_semester(school_year_id) if current_year else []
        else:
            semesters = dao.get_semester(current_year.id) if current_year else []
    else:  # Role = TEACHER
        class_name = dao.get_class_by_homeroom_teacher_id(current_user.user.id)
        if not class_name:
            flash("Bạn không phải giáo viên chủ nhiệm nên không có quyền truy cập báo cáo thống kê theo lớp.", "danger")
            return redirect(url_for('get_home_page'))
        current_year = dao.get_current_school_year()
        semesters = dao.get_semester(current_year.id) if current_year else []
        students = dao.get_student_ids_by_class_id(class_name.id, semester_id)
        school_years = []
        classes = []



    return render_template('admin/class-summary.html', semester_id=semester_id, class_id=class_id,
                           school_year_id=school_year_id,
                           class_name=class_name, current_year=current_year, semesters=semesters, students=students,
                           school_years=school_years, classes=classes)


@app.route("/students/<int:student_id>")
def student_detail(student_id):
    student = dao.get_student_by_id(student_id)

    return render_template('admin/student-detail.html', student=student)


@app.route("/students/update/<int:student_id>", methods=['get', 'post'])
def student_update(student_id):
    student = dao.get_student_by_id(student_id)
    if request.method.__eq__('POST'):
        name = request.form.get('name')
        address = request.form.get('address')
        email = request.form.get('email')
        date_of_birth = request.form.get('date_of_birth')
        phone_number = request.form.get('phone_number')

        # Gọi hàm validate từ dao
        if not dao.validate_input(name, address, phone_number, email):
            return redirect(url_for('student_update', student_id=student_id))

        dao.update_student(student_id, name=name,
                           address=address,
                           email=email,
                           date_of_birth=date_of_birth,
                           phone_number=phone_number)
        return redirect(url_for('student_update', student_id=student_id))

    return render_template('admin/update-student.html', student=student)


@app.route("/students/delete/<int:student_id>", methods=['get', 'post'])
def student_delete(student_id):
    student = dao.get_student_by_id(student_id)
    if request.method.__eq__('POST'):
        try:
            dao.delete_student(student_id)
            return redirect(url_for('find_student_page'))
        except Exception as e:
            flash(f"Lỗi: {str(e)}", "danger")
            return redirect(url_for('find_student_page'))
    return render_template('admin/delete-student.html', student=student)


@app.route("/list-subject/add-subject", methods=['get', 'post'])
def add_new_subject():
    if request.method.__eq__('POST'):
        name = request.form.get('subject_name')
        if dao.handel_save_subject(name):
            flash("Môn học đã có trong hệ thống!", "warning")
            return redirect(url_for('add_new_subject'))
        dao.save_subject(name)
        flash("Thêm môn học thành công!", "success")
    return render_template('admin/add-subject.html')


@app.route('/my-account/<int:id>', methods=['GET', 'POST'])
def account_detail(id):
    user = dao.find_user(id)
    return render_template('admin/detail-account.html', user=user)


if __name__ == '__main__':
    from qlhsapp.admin import *

    app.run(debug=True)
