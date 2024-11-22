# DAO chứa các phương thức tương tác xuống CSDL
from flask import flash

from qlhsapp import app, db
from qlhsapp.models import ScoreType, Score, Regulation


def load_score_regulation():
    return ScoreType.query.all()


def check_exist_score_type(score_type):
    existing_score_type = ScoreType.query.filter_by(name=score_type).first()
    return existing_score_type


def handle_add_score_regulation(score_type, score_quantity, coefficient):
    if score_quantity < 1 or score_quantity > 10 or coefficient < 1 or coefficient > 10:
        flash('Hệ số và cột điểm phải trong khoảng từ 1 đến 10', 'warning')
        return False
    if check_exist_score_type(score_type):
        flash('Loại điểm này đã tồn tại!!!', 'danger')
        return False

    new_score_type = ScoreType(name=score_type,
                               score_quantity=score_quantity,
                                coefficient=coefficient)
    db.session.add(new_score_type)
    db.session.commit()
    flash('Thêm loại điểm mới thành công!', 'success')
    return True


def get_score_type_by_name(name):
    return ScoreType.query.filter_by(name=name).first()

def update_score_regulation(score_type, score_quantity, coefficient):
    st = check_exist_score_type(score_type)
    if st:
        st.score_quantity = int(score_quantity)
        st.coefficient = int(coefficient)
        db.session.commit()
        return True

def update_regulation(key_name, value):
    if value > 100 or value < 10:
        flash('Sĩ số phải trong khoảng từ 10 đến 100', 'warning')
        return False
    regulation = Regulation.query.filter_by(key_name=key_name).first()
    if regulation:
        regulation.value = value
        db.session.commit()
        flash('Cập nhật sĩ số tối đa thành công!', 'success')
        return True



