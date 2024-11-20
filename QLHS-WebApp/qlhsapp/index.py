
from flask import render_template, request, url_for, redirect
from qlhsapp.models import ScoreRegulation, ScoreType
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

            print(st.id)   # tại sao không có dòng này thì lại báo lỗi NoneType st.id nhỉ??????
            score_id = st.id
            # trong ScoreRegulation chỉ có trường score_type_id nên phải tìm đối tượng qua score_type để lấy id
            score_regulation = ScoreRegulation.query.filter_by(score_type_id=score_id).first()
            if score_regulation: #Thay thi cap nhat
                score_regulation.score_quantity = int(score_quantity)
                score_regulation.coefficient = int(coefficient)

                db.session.commit()

        return redirect(url_for('score_regulations_page'))

    score_regulation = dao.load_score_regulation()
    return render_template('admin/score.html', score_regulation=score_regulation)



@app.route("/add-new-score-type", methods=['get', 'post'])
def new_score_regulation():
    # score_type = request.form.get('scoreType')
    # score_quantity = request.form.get('scoreQuantity')
    # coefficient = request.form.get('coefficient')
    #
    # dao.add_score_regulation(score_type, int(score_quantity), int(coefficient))
    return render_template('admin/new-score-regulation.html')




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
