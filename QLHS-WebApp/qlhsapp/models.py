from os.path import realpath

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Enum, Boolean, Float
from qlhsapp import db, app
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from datetime import datetime


# Models chứa các class là các table trong CSDL

class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class UserRole(PyEnum):
    ADMIN = 'ADMIN'
    STAFF = 'STAFF'
    TEACHER = 'TEACHER'


# Loai diem
class ScoreType(PyEnum):
    FIFTEEN = 1  # 15p
    FORTY_FIVE = 2  # 45p
    END_TERM = 3  # Cuoi ky



class GenderEnum(PyEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"


class Status(PyEnum):
    CREATE = 'CREATE'
    EDIT = 'EDIT'




class User(BaseModel):
    first_name = Column(String(20), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    phone_number = Column(String(12), nullable=False)
    address = Column(String(255))
    avatar = Column(String(255))
    # Create by Administrator's id
    create_by_Id = Column(Integer, ForeignKey('administrator.admin_id'), nullable=False)

    # OneToOne, uselist=False: Chi dinh moi quan he 1-1
    account = relationship('Account', back_populates='user', uselist=False) # done
    staff = relationship('Staff', back_populates='user', uselist=False) # done
    teacher = relationship('Teacher', back_populates='user', uselist=False) # done
    # 1-1: An user can be an admin
    administrator = relationship('Administrator', back_populates='user', uselist=False) # done
    # 1-N: User are managed by an admin
    admin_creator = relationship('Administrator', back_populates='manage_users') # done


# Tai khoan
class Account(db.Model):
    account_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_date = Column(DateTime, default=datetime.now())
    active = Column(Boolean, default=True)

    # OneToOne voi User
    user = relationship('User', back_populates='account') # done


# Nhan vien
class Staff(db.Model):
    staff_id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    user = relationship('User', back_populates='staff') # done

    classes = relationship('Class', secondary='StaffClass', back_populates='staff') # done

    students = relationship('Student', back_populates='staff')


# Quan tri vien
class Administrator(db.Model):
    admin_id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    user = relationship('User', back_populates='administrator', uselist=False) # done
    # 1 - N: An admin manages many users
    manage_users = relationship('User', back_populates='admin_creator') # done
    # 1 - N: An admin manages many subjects
    create_subject = relationship('Subject', back_populates='admin_creator') # done


student_class = db.Table('student_class',
                         Column('id', Integer, primary_key=True, autoincrement=True),
                         Column('student_id', Integer, ForeignKey('student.id')),
                         Column('class_id', Integer, ForeignKey('class.id'))
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



# Staff_Class, Many-To-Many
class StaffClass(BaseModel):
    staff_id = Column(Integer, ForeignKey('staff.staff_id'), nullable=False)
    class_id = Column(Integer, ForeignKey('class.id'), nullable=False)
    date_time = Column(DateTime, default=datetime.now())
    status = Column(Enum(Status), nullable=False)




# Giao vien
class Teacher(db.Model):
    teacher_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    homeroom_class_id = Column(Integer, ForeignKey('class.id'), nullable=True)
    # 1 - 1: teacher homeroom
    homeroom_class = relationship('Class', back_populates='homeroom_teacher', uselist=False) # done
    # 1 - 1: An user can be a teacher
    user = relationship('User', back_populates='teacher', uselist=False) # done
    # N - N: A teacher teach many subjects
    subjects = relationship('Subject', secondary='teacher_subject', back_populates='teachers') # done
    # N - N: A teacher teach many classes
    teach_classes = relationship('Class', secondary='teacher_class', back_populates='teachers') # done
    # 1 - N: A teacher enter scores for many scoreboards
    enter_scores = relationship('ScoreBoard', back_populates='teacher') # done


class Class(BaseModel):
    name = Column(String(20), nullable=False, unique=True)
    grade_level_id = Column(Integer, ForeignKey('grade_level.id'), nullable=False)
    grade_level = relationship('GradeLevel', back_populates='classes') # done
    # this class is homeroom_ed by this teacher ;)
    homeroom_teacher_id = Column(Integer, ForeignKey('teacher.teacher_id'), nullable=False)
    # N - N: Subject teachers
    teachers = relationship('Teacher', secondary='teacher_class', back_populates='teach_classes') # done
    # N - N: Students
    students = relationship('Student', secondary='student_class', back_populates='classes') # done
    # N - N: A class is homeroom_ed by one teacher
    homeroom_teacher = relationship('Teacher', back_populates='homeroom_class') # done

    staff = relationship('Staff', secondary='StaffClass', back_populates='classes') # done




# # Quy dinh
# class Regulation(BaseModel):
#     pass


# Khoi lop
class GradeLevel(BaseModel):
    __tablename__ = 'grade_level'
    name = Column(String(50), nullable=False)
    classes = relationship('Class', back_populates='grade_level', lazy=True) # done









class Student(BaseModel):
    name = Column(String(50), nullable=False)
    address = Column(String(100))
    email = Column(String(50))
    gender = Column(Enum(GenderEnum, name="gender_enum"), nullable=False)
    phone_number = Column(String(10))
    date_of_birth = Column(Date, nullable=False)
    staff_id = Column(Integer, ForeignKey('staff.staff_id'), nullable=False)
    # N - N: A student can study in many classes
    classes = relationship('Class', secondary='student_class', back_populates='students', lazy=True) # done
    # 1 - N: A student is admitted by one user (staff)
    staff = relationship('Staff', back_populates='students') # done
    # 1 - N: A student has many scoreboards
    score_boards = relationship('ScoreBoard', back_populates='student') # done


# Bang diem
class ScoreBoard(BaseModel):
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subject.id'), nullable=False)
    semester_id = Column(Integer, ForeignKey('semester.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teacher.teacher_id'), nullable=False)
    # 1 - N: A subject's scoreboard has many scores
    scores = relationship('Score', back_populates='score_board') # done
    # 1 - N: A scoreboard is scored by a teacher
    teacher = relationship('Teacher', back_populates='enter_scores') # done
    # 1 - N: A scoreboard belongs to a student
    student = relationship('Student', back_populates='score_boards') # done



# Diem
class Score(BaseModel):
    score_type = Column(Enum(ScoreType), nullable=False)
    score_value = Column(Float, nullable=False)
    score_board_id = Column(Integer, ForeignKey('score_board.id'), nullable=False)
    # 1 - N: A score belongs to one scoreboard
    score_board = relationship('ScoreBoard', back_populates='scores') # done



# Cau hinh so cot diem
class ScoreConfig(BaseModel):
    score_type = Column(Enum(ScoreType), nullable=False)
    score_quantity = Column(Integer, nullable=False)



# Mon hoc
class Subject(BaseModel):
    name = Column(String(50), unique=True, nullable=False)
    creator_admin_id = Column(Integer, ForeignKey('administrator.admin_id'), nullable=False)
    admin_creator = relationship('Administrator', back_populates='create_subject') # done
    # N - N
    teachers = relationship('Teacher', secondary='teacher_subject', back_populates='subjects') # done


# Hoc Ky
class Semester(BaseModel):
    name = Column(String(20), nullable=False)
    school_year = Column(String(10), nullable=False)




if __name__ == '__main__':
    with app.app_context():
        db.create_all()
