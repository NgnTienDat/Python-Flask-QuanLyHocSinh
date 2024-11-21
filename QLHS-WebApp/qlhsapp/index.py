from flask import render_template, request, redirect, jsonify, url_for
from sqlalchemy import except_

from qlhsapp import app
import dao
import sqlite3

# Index là Controller: Định tuyến các action


@app.route("/")
def get_home_page():
    return render_template('admin/index.html')


@app.route("/login")
def get_login_page():
    return render_template('login.html')


# Trung code: Tra cuu hoc sinh
@app.route("/find-student")
def find_student_page():
    kw = request.args.get('kw')
    students = dao.load_students(kw=kw)
    return render_template('admin/find-student.html', students=students)

@app.route("/delete-student")
def delete_student(id):
    try:
        dao.delete_student_from_db(id)
        return jsonify({"success": True}), 200
    except Exception as e:
        print(e)
        return jsonify({"success": False}), 500


@app.route('/edit-student/<int:id>')
def edit_student(id):
    conn = dao.get_db_connection()
    student = conn.execute('SELECT * FROM student WHERE id = ?', (id,)).fetchone()
    conn.close()
    if student:
        return render_template('admin/update-student.html', student=student)
    return "Không tìm thấy học sinh", 404

# Route để cập nhật thông tin khách hàng
@app.route('/update-student/<int:id>', methods=['GET', 'POST'])
def update_student(id):
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        gender = request.form['gender']
        date_of_birth = request.form['date_of_birth']
        email = request.form['email']
        phone_number = request.form['phone_number']

        # Chuyển đổi gender
        if gender == 'Nam':
            gender = 'MALE'
        else:
            gender = 'FEMALE'

        conn = dao.get_db_connection()
        conn.execute('''UPDATE student SET name = ?, address = ?, gender = ?, date_of_birth = ?, email = ?
            , phone_number = ? WHERE id = ?''',
                     (name, address, gender, date_of_birth, email, phone_number, id))
        conn.commit()
        conn.close()
        return redirect(url_for('get_home_page'))  # Chuyển hướng về trang chủ sau khi cập nhật thành công

    return render_template('admin/update-student.html')



# Tiếp nhận học sinh
@app.route("/add-student", methods=['GET', 'POST'])
def add_student_page():
    if request.method == 'POST':
        name = request.form['name']
        address = request.form['address']
        gender = request.form['gender']
        date_of_birth = request.form['date_of_birth']
        email = request.form['email']
        phone_number = request.form['phone_number']
        staff_id = 1

        # Chuyển đổi gender
        if gender == 'Nam':
            gender = 'MALE'
        else:
            gender = 'FEMALE'

        connection = sqlite3.connect('./data/database.db')
        cursor = connection.cursor()
        cursor.execute("""
                    INSERT INTO student (name, address, gender, date_of_birth, email, phone_number, staff_id) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, address, gender, date_of_birth, email, phone_number, staff_id))
        connection.commit()
        connection.close()

        # Chuyển hướng về trang chính sau khi thêm thành công
        return redirect('/')

    return render_template('admin/add-student.html')

# Phân lớp học sinh
@app.route("/set-class")
def set_class_page():
    return render_template('admin/set-class.html')


# Quy định số cột điểm
@app.route("/score-regulation")
def score_regulations_page():
    return render_template('admin/score.html')


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


if __name__ == '__main__':
    from qlhsapp.admin import *

    app.run(debug=True)
