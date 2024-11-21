
from flask import render_template, request, url_for, redirect, flash
from qlhsapp.models import ScoreType, Score
from qlhsapp import app,db
import dao



@app.route("/")
def get_home_page():
    return render_template('admin/index.html')


@app.route("/login")
def get_login_page():
    return render_template('login.html')


# Trung code: Tra cuu hoc sinh
@app.route("/find-student")
def find_student_page():
    return render_template('admin/find-student.html')


# Tiếp nhận học sinh
@app.route("/add-student")
def add_student_page():
    return render_template('admin/add-student.html')


# Phân lớp học sinh
@app.route("/set-class")
def set_class_page():
    return render_template('admin/set-class.html')


# Quy định số cột điểm
@app.route("/score-regulation", methods=['get', 'post'])
def score_regulations_page():
    # Update score regulation changes
    if request.method.__eq__('POST'):
        scores_update = []
        for index in range(1, len(request.form)//3+1):  # chia nguyen de lay so dong, vi du 9 o input thi 9//3=3 dong, lap tung dong
            score_type = request.form.get(f'score_type_{index}')
            score_quantity = request.form.get(f'score_quantity_{index}')
            coefficient = request.form.get(f'coefficient_{index}')

            scores_update.append({
                'score_type':score_type,
                'score_quantity':score_quantity,
                'coefficient':coefficient
            })

        for data in scores_update:
            score_type = data['score_type'] # chỉ gửi lên chuỗi ví dụ '15 phút'
            score_quantity=data['score_quantity']
            coefficient=data['coefficient']

            st = ScoreType.query.filter_by(name=score_type).first()
            if st: #Thay thi cap nhat
                st.score_quantity = int(score_quantity)
                st.coefficient = int(coefficient)

                db.session.commit()

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
@app.route("/numbers-regulation")
def numbers_regulations_page():
    return render_template('admin/numbers.html')


# Quy định tuổi
@app.route("/age-regulation")
def age_regulations_page():
    return render_template('admin/age.html')


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


@app.route("/list-subject")
def list_subject():
    return render_template('admin/subject.html')


@app.route("/list-class")
def list_class():
    return render_template('admin/class.html')


@app.route("/list-user")
def list_user():
    return render_template('admin/list-user.html')


@app.route("/subject-summary-score")
def subject_summary_score():
    return render_template('admin/subject-summary.html')


@app.route("/class-summary-score")
def class_summary_score():
    return render_template('admin/class-summary.html')


if __name__ == '__main__':
    from qlhsapp.admin import *

    app.run(debug=True)
