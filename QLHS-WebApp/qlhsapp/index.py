from flask import render_template
from qlhsapp import app
import dao



if __name__ == '__main__':
    from qlhsapp.admin import *
    app.run(debug=True)
