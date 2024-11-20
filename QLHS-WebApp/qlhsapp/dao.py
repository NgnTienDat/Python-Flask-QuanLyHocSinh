# DAO chứa các phương thức tương tác xuống CSDL
from qlhsapp import app, db
from qlhsapp.models import ScoreRegulation

def load_score_regulation():
    return ScoreRegulation.query.all()