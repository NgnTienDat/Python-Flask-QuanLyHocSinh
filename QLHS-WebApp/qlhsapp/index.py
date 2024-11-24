from flask import render_template, request, redirect, url_for, flash
from qlhsapp import app, db, login_manager
import dao
from flask_login import login_user, logout_user


# Index là Controller: Định tuyến các action


@app.route("/")
def get_home_page():
    return render_template('admin/index.html')


@login_manager.user_loader
def get_user_by_id(user_id):
    return dao.get_account_by_id(user_id)


@app.route("/login", methods=['get', 'post'])
def login_process():
    if request.method.__eq__("POST"):
        username = request.form.get('username')
        password = request.form.get('password')
        user = dao.auth_account(username=username, password=password)
        if user:
            login_user(user)
            return redirect('/')

    return render_template('login.html')


@app.route("/logout")
def logout_process():
    logout_user()
    return redirect('/login')


@app.route('/register', methods=['get', 'post'])
def register_process():
    err_msg = ''
    user_id = request.args.get('user_id')
    if request.method.__eq__('POST'):
        username = request.form.get('registerUsername')
        password = request.form.get('registerPassword')
        confirm = request.form.get('confirmPassword')
        role = request.form.get('user_role')
        user_id = request.form.get('user_id')
        account_id = user_id
        print(f"User ID from URL: {user_id}")  # In ra giá trị user_id từ query string
        # Kiểm tra xem mật khẩu có khớp không
        if password == confirm:
            if password and username:  # Kiểm tra nếu mật khẩu và tài khoản không phải là None
                try:
                    # Thêm người dùng vào cơ sở dữ liệu với mật khẩu đã mã hóa
                    dao.add_account(account_id=account_id, username=username, password=password, role=role)
                    return redirect('/login')  # Chuyển hướng đến trang quản lý người dùng
                except Exception as e:
                    err_msg = f"Lỗi khi thêm tài khoản: {str(e)}"
            else:
                err_msg = 'Vui lòng nhập đầy đủ thông tin tài khoản và mật khẩu.'
        else:
            err_msg = 'Mật khẩu không khớp!'

    return render_template('register.html', err_msg=err_msg, user_id=user_id)



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
    kw = request.args.get('kw')
    users = dao.load_users(kw=kw)
    return render_template('admin/list-user.html', users=users)


@app.route("/delete-user/<int:id>", methods=['DELETE'])
def delete_user(id):
    try:
        dao.delete_user_from_db(id)
        print("Xóa thành công")
        return {"message": "Xóa thành công"}
    except Exception as e:
        print("Xóa thất bại")


# Route để cập nhật thông tin khách hàng
@app.route('/update-user/<int:id>', methods=['GET', 'POST'])
def update_user(id):
    """
        Cập nhật thông tin người dùng dựa trên ID.

        :param id: ID của người dùng cần cập nhật
        """
    user = dao.find_user(id)  # Lấy thông tin người dùng theo ID

    if request.method == 'POST':
        # Lấy dữ liệu từ form
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        email = request.form['email']
        phone_number = request.form['phone_number']

        # Cập nhật thông tin người dùng
        user.first_name = first_name
        user.last_name = last_name
        user.address = address
        user.email = email
        user.phone_number = phone_number

        try:
            # Lưu thay đổi vào database
            db.session.commit()
            print(f"Đã cập nhật thông tin người dùng có ID {id} thành công.")
            return redirect(url_for('get_home_page'))  # Chuyển hướng về trang chủ
        except Exception as e:
            db.session.rollback()
            print(f"Lỗi khi cập nhật thông tin người dùng có ID {id}: {e}")

    # Truyền thông tin người dùng vào template để hiển thị
    return render_template('admin/update-user.html', user=user)


@app.route("/add-user", methods=['GET', 'POST'])
def add_user_page():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address = request.form['address']
        email = request.form['email']
        phone_number = request.form['phone_number']

        try:
            user_id = dao.add_user(first_name=first_name, last_name=last_name, address=address, email=email,
                                   phone_number=phone_number, avatar=request.files.get('avatar'))
            return redirect(url_for('register_process', user_id=user_id))
        except ValueError as e:
            # Hiển thị lỗi chi tiết cho người dùng
            flash(str(e), 'error')  # Dùng flash để hiển thị lỗi
        except Exception as e:
            flash("Lỗi khi thêm người dùng", 'error')
            print(f"Lỗi chi tiết: {e}")

    return render_template('admin/add-user.html')

if __name__ == '__main__':
    from qlhsapp.admin import *

    app.run(debug=True)
