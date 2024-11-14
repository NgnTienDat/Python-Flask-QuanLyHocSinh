from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Boolean, Table
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from qlhsapp import db, app
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
    FORTY_FIVE = 2 # 45p
    END_TERM = 3  # Cuoi ky


class User(BaseModel):
    first_name = Column(String(20), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    phone_number = Column(String(12), nullable=False)
    address = Column(String(255))
    avatar = Column(String(255))

    # OneToOne, uselist=False: Chi dinh moi quan he 1-1
    account = relationship('Account', back_populates='user', uselist=False)
    staff = relationship('Staff', back_populates='user', uselist=False)
    teacher = relationship('Teacher', back_populates='user', uselist=False)
    administrator = relationship('Administrator', back_populates='user', uselist=False)



# Tai khoan
class Account(db.Model):
    account_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_date = Column(DateTime, default=datetime.now())
    active = Column(Boolean, default=True)

    # OneToOne voi User
    user = relationship('User', back_populates='account')



# Nhan vien
class Staff(db.Model):
    staff_id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    user = relationship('User', back_populates='staff')



# Quan tri vien
class Administrator(db.Model):
    admin_id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    user = relationship('User', back_populates='administrator', uselist=False)



# Giao vien
class Teacher(db.Model):

    teacher_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    # OneToOne
    user = relationship('User', back_populates='teacher', uselist=False)
    # ManyToMany
    subjects = relationship('Subject', secondary='teacher_subject', back_populates='teacher')




# # Quy dinh
# class Regulation(BaseModel):
#     pass
#
#
#
# class Student(BaseModel):
#     pass
#
#
# # Khoi lop
# class GradeLevel(BaseModel):
#     pass
#
#
#
# class Class(BaseModel):
#     pass
#
#
# # Bang diem
# class ScoreBoard(BaseModel):
#     pass
#
#
# # Diem
# class Score(BaseModel):
#     pass
#

# Mon hoc
class Subject(BaseModel):
    name = Column(String(50), unique=True, nullable=False)
    # ManyToMany
    teachers = relationship('Teacher', secondary='teacher_subject', back_populates='subject')



#
# # Hoc Ky
# class Semester(BaseModel):
#     pass
#
#
# # Staff_Class, Many-To-Many
# class StaffClass(BaseModel):
#     pass
#
# # Student_Class, Many-To-Many
# class StudentClass(BaseModel):
#     pass

# Teacher_Subject, Many-To-Many
teacher_subject = Table('teacher_subject', db.Model.metadata,
                        Column('id', Integer, primary_key=True, autoincrement=True),
                        Column('teacher_id', Integer, ForeignKey('teacher.teacher_id')),
                        Column('subject_id', Integer, ForeignKey('subject.id'))
)



if __name__=='__main__':
    with app.app_context():
        db.create_all()
