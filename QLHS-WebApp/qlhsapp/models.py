from sqlalchemy import Column, Integer, String, Enum
from qlhsapp import db
from enum import Enum


# Models chứa các class là các table trong CSDL

class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class UserRole(Enum):
    ADMIN = 1
    STAFF = 2
    TEACHER = 3


# Loai diem
class ScoreType(Enum):
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


class Student(BaseModel):
    pass


# Khoi lop
class GradeLevel(BaseModel):
    pass


class Class(BaseModel):
    pass


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


# Student_Class, Many-To-Many
class StudentClass(BaseModel):
    pass


# Teacher_Subject, Many-To-Many
class TeacherSubject(BaseModel):
    pass
