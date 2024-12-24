import hashlib

from cloudinary.uploader import remove_all_tags

from flask_login import UserMixin

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Date, Enum, Boolean, Float

from qlhsapp import db, app, engine
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from datetime import datetime


class BaseModel(db.Model):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)


class UserRole(PyEnum):
    ADMIN = 'ADMIN'
    STAFF = 'STAFF'
    TEACHER = 'TEACHER'

    def __str__(self):
        return self.value


# Gioi tinh
class GenderEnum(PyEnum):
    MALE = "MALE"
    FEMALE = "FEMALE"

    def __str__(self):
        return self.value


class Action(PyEnum):
    CREATE = 'CREATE'
    EDIT = 'EDIT'

    def __str__(self):
        return self.value


class User(BaseModel, UserMixin):
    first_name = Column(String(20), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    phone_number = Column(String(12), nullable=False)
    address = Column(String(255))
    avatar = Column(String(255), default="https://res.cloudinary.com/derx1izam/image/upload/v1733139904/u1znxkazv1qst2w908tr.jpg")
    # Create by Administrator's id
    create_by_Id = Column(Integer, ForeignKey('administrator.admin_id'), nullable=True)

    # OneToOne, uselist=False: Chi dinh moi quan he 1-1
    account = relationship('Account', back_populates='user', uselist=False)  # done
    staff = relationship('Staff', back_populates='user', uselist=False)  # done
    teacher = relationship('Teacher', back_populates='user', uselist=False)  # done
    # 1-1: An user can be an admin
    administrator = relationship('Administrator', back_populates='user', uselist=False,
                                 foreign_keys='Administrator.admin_id')  # done
    # 1-N: User are managed by an admin
    admin_creator = relationship('Administrator', back_populates='manage_users',
                                 foreign_keys=[create_by_Id])  # done

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


# Tai khoan
class Account(db.Model, UserMixin):
    account_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(50), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    created_date = Column(DateTime, default=datetime.now())
    active = Column(Boolean, default=True)

    # OneToOne voi User
    user = relationship('User', back_populates='account')  # done

    # Phương thức để lấy ID người dùng
    def get_id(self):
        return str(self.account_id)


# Nhan vien
class Staff(db.Model):
    staff_id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    user = relationship('User', back_populates='staff')  # done

    classes = relationship('Class', back_populates='staff')  # done

    students = relationship('Student', back_populates='staff')


# Quan tri vien
class Administrator(db.Model):
    admin_id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    user = relationship('User', back_populates='administrator', uselist=False, foreign_keys=[admin_id])  # done
    # 1 - N: An admin manages many users
    manage_users = relationship('User', back_populates='admin_creator', foreign_keys='User.create_by_Id')  # done

    # # 1 - N: An admin manages many subjects
    # create_subject = relationship('Subject', back_populates='admin_creator')  # done


class StudentClass(BaseModel):
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    class_id = Column(Integer, ForeignKey('class.id'), nullable=False)
    is_active = Column(Boolean, default=True)

    students = relationship('Student', back_populates='student_classes')
    classes = relationship('Class', back_populates='student_classes')


class TeachingAssignment(BaseModel):
    teacher_id = Column(Integer, ForeignKey('teacher.teacher_id'), nullable=False)
    class_id = Column(Integer, ForeignKey('class.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subject.id'), nullable=False)
    school_year_id = Column(Integer, ForeignKey('school_year.id'), nullable=False)

    teacher = relationship('Teacher', back_populates='teaching_assignment')
    class_ = relationship('Class', back_populates='teaching_assignment')
    subject = relationship('Subject', back_populates='teaching_assignment')
    school_year = relationship('SchoolYear', back_populates='teaching_assignment')


# Giao vien
class Teacher(db.Model):
    teacher_id = Column(Integer, ForeignKey('user.id'), primary_key=True)

    subject_id = Column(Integer, ForeignKey('subject.id'), nullable=True)

    is_homeroom_teacher = Column(Boolean, default=False)
    # 1 - 1: teacher homeroom
    homeroom_class = relationship('Class', back_populates='homeroom_teacher', uselist=False,
                                  foreign_keys='Class.homeroom_teacher_id')  # done
    # 1 - 1: An user can be a teacher
    user = relationship('User', back_populates='teacher', uselist=False)  # done
    # N - N: A teacher teach many subjects
    subject = relationship('Subject', back_populates='teachers')  # done

    # 1 - N: A teacher enter scores for many scoreboards
    enter_scores = relationship('ScoreBoard', back_populates='teacher')  # done
    teaching_assignment = relationship('TeachingAssignment', back_populates='teacher')

    def __str__(self):
        return self.name


class Class(BaseModel):
    name = Column(String(20), nullable=False, unique=True)
    grade_level_id = Column(Integer, ForeignKey('grade_level.id'), nullable=False)
    # Number of students (Sĩ số)
    student_numbers = Column(Integer, nullable=True)

    school_year_id = Column(Integer, ForeignKey('school_year.id'), nullable=False)

    staff_id = Column(Integer, ForeignKey('staff.staff_id'), nullable=False)

    school_year = relationship('SchoolYear', back_populates='classes')  # done

    grade_level = relationship('GradeLevel', back_populates='classes')  # done
    # this class is homeroom_ed by this teacher ;)
    homeroom_teacher_id = Column(Integer, ForeignKey('teacher.teacher_id'), unique=True, nullable=False)

    # 1 - 1: A class is homeroom_ed by one teacher
    homeroom_teacher = relationship('Teacher', back_populates='homeroom_class',
                                    foreign_keys=[homeroom_teacher_id])  # done

    staff = relationship('Staff', back_populates='classes')  # done

    student_classes = relationship('StudentClass', back_populates='classes')
    teaching_assignment = relationship('TeachingAssignment', back_populates='class_')

    def __str__(self):
        return self.name


# Khoi lop
class GradeLevel(BaseModel):
    __tablename__ = 'grade_level'
    name = Column(String(50), nullable=False)
    classes = relationship('Class', back_populates='grade_level', lazy=True)  # done


class Student(BaseModel):
    name = Column(String(50), nullable=False)
    address = Column(String(100))
    email = Column(String(50))
    gender = Column(Enum(GenderEnum, name="gender_enum"), nullable=False)
    phone_number = Column(String(10))
    date_of_birth = Column(Date, nullable=False)
    in_assigned = Column(Boolean, default=False)  # Da duoc phan vao lop hay chua

    staff_id = Column(Integer, ForeignKey('staff.staff_id'), nullable=False)
    # N - N: A student can study in many classes

    # 1 - N: A student is admitted by one user (staff)
    staff = relationship('Staff', back_populates='students')  # done
    # 1 - N: A student has many scoreboards
    score_boards = relationship('ScoreBoard', back_populates='student', cascade="all, delete")  # done

    student_classes = relationship('StudentClass', back_populates='students', cascade="all, delete")


# Bang diem
class ScoreBoard(BaseModel):
    student_id = Column(Integer, ForeignKey('student.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subject.id'), nullable=False)
    semester_id = Column(Integer, ForeignKey('semester.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teacher.teacher_id'), nullable=False)
    average_score = Column(Float, nullable=True, default=0)  # Thêm cột average_score
    # 1 - N: A subject's scoreboard has many scores
    scores = relationship('Score', back_populates='score_board', cascade="all, delete")  # done
    # 1 - N: A scoreboard is scored by a teacher
    teacher = relationship('Teacher', back_populates='enter_scores')  # done
    # 1 - N: A scoreboard belongs to a student
    student = relationship('Student', back_populates='score_boards')  # done
    # 1 - N: A scoreboard belongs to a subject
    subject = relationship('Subject', back_populates='score_boards')  # done
    # 1 - N: A scoreboard belongs to one semester
    semester = relationship('Semester', back_populates='score_boards')  # done


# Diem
class Score(BaseModel):
    score_type = Column(Integer, ForeignKey('score_type.id'), nullable=True)
    score_value = Column(Float, nullable=False)
    index = db.Column(db.Integer, nullable=False)  # Add this column
    score_board_id = Column(Integer, ForeignKey('score_board.id'), nullable=False)
    # 1 - N: A score belongs to one scoreboard
    score_board = relationship('ScoreBoard', back_populates='scores')  # done


# Cau hinh so cot diem
class ScoreType(BaseModel):
    name = Column(String(30), nullable=False, unique=True)
    score_quantity = Column(Integer, nullable=False)
    # Hệ số
    coefficient = Column(Integer, nullable=False)


# Quy dinh
class Regulation(BaseModel):
    key_name = Column(String(50), unique=True, nullable=False)
    value = Column(String(50), unique=True)


# Nam hoc
class SchoolYear(BaseModel):
    name = Column(String(50), unique=True, nullable=False)
    # 1 - N: A school year has two semesters
    semesters = relationship('Semester', back_populates='school_year')  # done
    classes = relationship('Class', back_populates='school_year')  # done
    teaching_assignment = relationship('TeachingAssignment', back_populates='school_year')

    def __str__(self):
        return self.name


# Mon hoc
class Subject(BaseModel):
    name = Column(String(50), unique=True, nullable=False)
    # creator_admin_id = Column(Integer, ForeignKey('administrator.admin_id'), nullable=False)
    # admin_creator = relationship('Administrator', back_populates='create_subject')  # done
    # N - N
    teachers = relationship('Teacher', back_populates='subject')  # done
    # 1 - N: A subject has many scoreboards
    score_boards = relationship('ScoreBoard', back_populates='subject')  # done
    teaching_assignment = relationship('TeachingAssignment', back_populates='subject')

    def __str__(self):
        return self.name


# Hoc Ky
class Semester(BaseModel):
    name = Column(String(20), nullable=False)
    school_year_id = Column(Integer, ForeignKey('school_year.id'), nullable=False)
    start_date = Column(Date, nullable=False)
    finish_date = Column(Date, nullable=False)

    # 1 - N: A semester belongs to one school year
    school_year = relationship('SchoolYear', back_populates='semesters')  # done
    # 1 - N: A semester has many scoreboard
    score_boards = relationship('ScoreBoard', back_populates='semester')  # done

    def __str__(self):
        return self.name


# from datetime import date
# from random import randint
# from sqlalchemy.orm import Session
#
#
# def create_students(session: Session):
#     # Danh sách các học sinh
#     students = []
#
#     # Tạo 33 học sinh nam
#     for i in range(33):
#         student = Student(
#             name=f"Nguyễn Văn Nam {i + 1}",
#             address="Hồ Chí Minh",
#             email=f"nam{i + 1}@example.com",
#             gender=GenderEnum.MALE,
#             phone_number=f"090{randint(1000000, 9999999)}",
#             date_of_birth=date(2005, randint(1, 12), randint(1, 28)),  # Ngày tháng ngẫu nhiên
#             staff_id=7
#         )
#         students.append(student)
#
#     # Tạo 33 học sinh nữ
#     for i in range(33):
#         student = Student(
#             name=f"Hà Kiều Nữ {i + 1}",
#             address="Hồ Chí Minh",
#             email=f"nu{i + 1}@example.com",
#             gender=GenderEnum.FEMALE,
#             phone_number=f"091{randint(1000000, 9999999)}",
#             date_of_birth=date(2005, randint(1, 12), randint(1, 28)),  # Ngày tháng ngẫu nhiên
#             staff_id=7
#         )
#         students.append(student)
#
#     # Thêm danh sách vào session
#     session.add_all(students)
#     session.commit()
#     print("Đã thêm 66 học sinh vào cơ sở dữ liệu.")

# def create_students(session: Session):
#     # Danh sách các đối tượng StudentClass
#     studentClasses = []
#
#     # Số lượng học sinh mỗi lớp
#     students_per_class = 11
#
#     # Tạo danh sách lớp
#     classes = [("10A1", 1), ("10A2", 2), ("10A3", 3), ("10A4", 4), ("10A5", 5), ("10A6", 6)]
#
#     # Biến đếm student_id
#     student_id = 1
#
#     for class_name, class_id in classes:
#         for i in range(students_per_class):
#             studentClass = StudentClass(
#                 student_id=student_id,  # Mỗi học sinh có ID duy nhất
#                 class_id=class_id  # ID của lớp học
#             )
#             studentClasses.append(studentClass)
#             student_id += 1  # Tăng ID cho học sinh tiếp theo
#
#     # Thêm danh sách vào session
#     session.add_all(studentClasses)
#     session.commit()
#     print("Đã thêm học sinh cho tất cả các lớp vào cơ sở dữ liệu.")


if __name__ == '__main__':
    with app.app_context():
        db.create_all()


        # with Session(engine) as session:  # Đảm bảo bạn đã kết nối đúng engine
        #     create_students(session)


        # import hashlib
        # u = User(first_name='Tran', last_name='Truong', email='admin@gmail.com', phone_number='0123456789', address='HT13, Hiệp Thành')
        # a = Account(account_id=u.id,username='admin',password=str(hashlib.md5('123456'.encode('utf-8')).hexdigest()),
        #          user_role=UserRole.ADMIN)
        # db.session.add(u)
        # db.session.add(a)
        # db.session.commit()