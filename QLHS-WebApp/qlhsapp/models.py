from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Enum, Boolean, Table
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



class GenderEnum(PyEnum):
    MALE = "male"
    FEMALE = "female"


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


student_class = db.Table('student_class',
                         Column('id', Integer, primary_key=True, autoincrement=True),
                         Column('student_id', Integer, ForeignKey('student.id'), primary_key=True),
                         Column('class_id', Integer, ForeignKey('class.id'), primary_key=True)
                         )


teacher_class = db.Table('teacher_class',
                         Column('id', Integer, primary_key=True, autoincrement=True),
                          Column('teacher_id', Integer, ForeignKey('teacher.teacher_id')),
                          Column('class_id', Integer, ForeignKey('class.id'))
                         )


# Teacher_Subject, Many-To-Many
teacher_subject = db.Table('teacher_subject',
                        Column('id', Integer, primary_key=True, autoincrement=True),
                        Column('teacher_id', Integer, ForeignKey('teacher.teacher_id')),
                        Column('subject_id', Integer, ForeignKey('subject.id'))
                        )



# # Staff_Class, Many-To-Many
# staff_class = db.Table('staff_class',
#                         Column('id', Integer, primary_key=True, autoincrement=True),
#                         Column('staff_id', Integer, ForeignKey('staff.staff_id')),
#                         Column('class_id', Integer, ForeignKey('class.id'))
#                         )



# Giao vien
class Teacher(db.Model):
    teacher_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    homeroom_class_id = Column(Integer, ForeignKey('class.id'), nullable=True)
    # 1 - 1: Homeroom
    homeroom_class = relationship('Class', back_populates='teacher', uselist=False)
    # 1 - 1: User
    user = relationship('User', back_populates='teacher', uselist=False)
    # N - N: Teach subjects
    subjects = relationship('Subject', secondary='teacher_subject', back_populates='teacher')
    # N - N: Teach classes
    teach_classes = relationship('Class', secondary='teacher_class', back_populates='teacher')



# # Quy dinh
# class Regulation(BaseModel):
#     pass


# Khoi lop
class GradeLevel(BaseModel):
    __tablename__ = 'grade_level'
    name = Column(String(50), nullable=False)
    classes = relationship('Class', backref='grade_level', lazy=True)







class Class(BaseModel):
    name = Column(String(20), nullable=False, unique=True)
    grade_level_id = Column(Integer, ForeignKey('grade_level.id'), nullable=False)
    # this class is homeroom_ed by this teacher ;)
    homeroom_teacher_id = Column(Integer, ForeignKey('teacher.teacher_id'), nullable=False)
    # N - N: Subject teachers
    subject_teachers = relationship('Teacher', secondary='teacher_class', back_populates='classes')
    # N - N: Students
    students = relationship('Student', secondary='student_class', back_populates='classes')




class Student(BaseModel):
    name = Column(String(50), nullable=False)
    address = Column(String(100))
    email = Column(String(50))
    gender = Column(Enum(GenderEnum, name="gender_enum"), nullable=False)
    phone_number = Column(String(10))
    date_of_birth = Column(Date, nullable=False)
    classes = relationship('Class', secondary='student_class', back_populates='students', lazy=True)



# Bang diem
# class ScoreBoard(BaseModel):
#     pass
#
#
# # Diem
# class Score(BaseModel):
#     pass


# Mon hoc
class Subject(BaseModel):
    name = Column(String(50), unique=True, nullable=False)
    # ManyToMany
    teachers = relationship('Teacher', secondary='teacher_subject', back_populates='subject')


# Hoc Ky
# class Semester(BaseModel):
#     pass
#
#





if __name__ == '__main__':
    with app.app_context():
        db.create_all()
