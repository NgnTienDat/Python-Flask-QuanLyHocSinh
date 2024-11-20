# DAO chứa các phương thức tương tác xuống CSDL
from qlhsapp import app, db
from qlhsapp.models import ScoreRegulation, ScoreType, Score


def load_score_regulation():
    return ScoreRegulation.query.all()

def add_score_regulation(score_type, score_quantity, coefficient):
    existing_score_type = ScoreType.query.filter_by(name=score_type).first()
    if existing_score_type:
        score_type_id = existing_score_type.id
    else:
        new_score_type = ScoreType(name=score_type)
        db.session.add(new_score_type)
        db.session.flush() # luu vao bo nho tam de lay ID cua score type
        score_type_id = new_score_type.id

    new_score_regulation = ScoreRegulation(score_type_id=score_type_id,
                                           score_quantity=score_quantity,
                                           coefficient=coefficient)

    db.session.add(new_score_regulation)
    db.session.commit()


def get_score_type_by_name(name):
    return ScoreType.query.filter_by(name=name).first()
