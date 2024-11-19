from flask import render_template
from qlhsapp import app


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
    return render_template('admin/find-student.html')


# Trung code: Tiep nhan hoc sinh
@app.route("/add-student")
def add_student_page():
    return render_template('admin/add-student.html')


if __name__ == '__main__':
    app.run(debug=True)
