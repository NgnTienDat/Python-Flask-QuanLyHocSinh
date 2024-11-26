import math

from flask import render_template, request, url_for, redirect, flash

from qlhsapp.models import ScoreType, Score, Regulation, Student, Teacher, GradeLevel, SchoolYear, Class, StudentClass

from qlhsapp import app, db
import dao


@app.route("/")
def get_home_page():
    return render_template('admin/index.html')


@app.route("/login")
def get_login_page():
    return render_template('login.html')


# Trung code: Tra cuu hoc sinh
@app.route("/students")
def find_student_page():
    kw = request.args.get("key-name")
    page = request.args.get("page", 1)
    stu = dao.load_student(kw=kw, page=int(page))
    counter = dao.count_student()
    return render_template('admin/find-student.html',
                           students=stu,
                           pages=math.ceil(counter / app.config['PAGE_SIZE']))


# Tiếp nhận học sinh
@app.route("/add-student")
def add_student_page():
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

    selected_class_id = request.args.get('class_id', type=int, default=0)
    if selected_class_id != 0:
        # Nếu đã chọn lớp, lấy danh sách học sinh của lớp đó
        student_class, pages = dao.load_student_in_assigned(selected_class_id, page=int(page))
        students = [sc.students for sc in student_class]
    else:
        students, pages = dao.load_student_no_assigned(page=int(page))

    return render_template('admin/set-class.html',
                           classes=classes, students=students, pages=pages, page=int(page),
                           total_unassigned_students=total_unassigned_students,
                           selected_class_id=selected_class_id)


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
    return render_template('admin/score.html', score_types=score_types)


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
    return render_template('admin/numbers.html', class_size=class_size)


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

    return render_template('admin/age.html', max_age=max_age, min_age=min_age)


# Nhập điểm
@app.route("/input-score")
def input_score():
    return render_template('admin/input-score.html')


# Xuất điểm
@app.route("/export-score")
def export_score():
    return render_template('admin/export-score.html')


@app.route("/list-teacher")
def list_teacher():
    return render_template('admin/teacher.html')

@app.route("/teacher-detail/<int:teacher_id>")
def teacher_detail(teacher_id):
    return render_template('admin/teacher-detail.html')


@app.route("/list-subject")
def list_subject():
    return render_template('admin/subject.html')


@app.route("/list-class")
def list_class():
    page = request.args.get('page', 1)
    grade_level_id = request.args.get('filter', 'all')  # mac dinh la lay tat ca

    classes, pages = dao.filter_class_by_grade_level_id(grade_level_id, page=int(page))

    grade_levels = GradeLevel.query.all()
    selected_filter = grade_level_id
    return render_template('admin/class.html', classes=classes,
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


@app.route("/list-user")
def list_user():
    return render_template('admin/list-user.html')


@app.route("/subject-summary-score")
def subject_summary_score():
    return render_template('admin/subject-summary.html')


@app.route("/class-summary-score")
def class_summary_score():
    return render_template('admin/class-summary.html')


@app.route("/students/<int:student_id>")
def student_detail(student_id):
    student = dao.get_student_by_id(student_id)

    return render_template('admin/student-detail.html', student=student)


@app.route("/students/update/<int:student_id>", methods=['get', 'post'])
def student_update(student_id):
    student = dao.get_student_by_id(student_id)
    if request.method.__eq__('POST'):
        dao.update_student(student_id, request.form.get('name'),
                           request.form.get('address'),
                           request.form.get('email'),
                           request.form.get('date_of_birth'),
                           request.form.get('phone_number'))
        flash("Student updated successfully!", "success")
        return redirect(url_for('find_student_page'))

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


if __name__ == '__main__':
    from qlhsapp.admin import *

    app.run(debug=True)
