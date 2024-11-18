from flask import render_template
from qlhsapp import app


# Index là Controller: Định tuyến các action


@app.route("/")
def get_home_page():
    return render_template('home-page-admin.html')


@app.route("/login")
def get_login_page():
    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)
