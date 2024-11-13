from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Enum
from qlhsapp import db, app
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from datetime import datetime


# Models chứa các class là các table trong CSDL

class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class UserRole(PyEnum):
    ADMIN = 1
    STAFF = 2
    TEACHER = 3


# Loai diem
class ScoreType(PyEnum):
    FIFTEEN = 1  # 15p
    FORTY_FIVE = 2  # 45p
    END_TERM = 3  # Cuoi ky


# Tai khoan
class Account(BaseModel):
    pass


class User(BaseModel):
    __abstract__ = True


# Nhan vien
class Staff(User):
    pass


# Giao vien
class Teacher(User):
    pass


# Quan tri vien
class Administrator(User):
    pass


# Quy dinh
class Regulation(BaseModel):
    pass


# Khoi lop
class GradeLevel(BaseModel):
    name = Column(String(50), nullable=False)
    classes = relationship('Class', backref='gradelevel', lazy=True)


student_class = db.Table('student_class',
                         Column('student_id', Integer, ForeignKey('student.id'), primary_key=True),
                         Column('class_id', Integer, ForeignKey('class.id'), primary_key=True)
                         )


class Class(BaseModel):
    name = Column(String(50), nullable=False)
    # teacher_id
    grade_id = Column(Integer, ForeignKey(GradeLevel.id), nullable=False)


class GenderEnum(PyEnum):
    MALE = "male"
    FEMALE = "female"


class Student(BaseModel):
    name = Column(String(50), nullable=False)
    address = Column(String(100))
    email = Column(String(50))
    gender = Column(Enum(GenderEnum, name="gender_enum"), nullable=False)
    phone_number = Column(String(10))
    date_of_birth = Column(Date, nullable=False)
    classes = relationship('Class', secondary='student_class',  backref='students', lazy=True)


# Bang diem
class ScoreBoard(BaseModel):
    pass


# Diem
class Score(BaseModel):
    pass


# Mon hoc
class Subject(BaseModel):
    pass


# Hoc Ky
class Semester(BaseModel):
    pass


# Staff_Class, Many-To-Many
class StaffClass(BaseModel):
    pass


# Teacher_Subject, Many-To-Many
class TeacherSubject(BaseModel):
    pass


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        db.session.commit()
