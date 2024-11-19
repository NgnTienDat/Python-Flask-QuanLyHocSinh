from flask import render_template
from qlhsapp import app
import dao


# Index là Controller: Định tuyến các action


@app.route("/")
def get_home_page():
    return render_template('home-page-admin.html')


@app.route("/login")
def get_login_page():
    return render_template('login.html')


@app.route('/admin/score-regulation')
def get_score_regulation_page():
    score_regulation = dao.load_score_regulation()

    return render_template('admin/regulations/score.html', score_regulation=score_regulation)


if __name__ == '__main__':
    from qlhsapp.admin import *
    app.run(debug=True)
