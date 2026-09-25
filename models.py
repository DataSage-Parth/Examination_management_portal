from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    contact_details = db.Column(db.String(255))
    department = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    examiner_profile = db.relationship(
        "ExaminerProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    examinations = db.relationship(
        "Examination",
        back_populates="assigned_examiner",
        foreign_keys="Examination.examiner_id"
    )
    slots = db.relationship(
        "ExaminationSlot",
        back_populates="examiner",
        cascade="all, delete-orphan"
    )
    bookings = db.relationship(
        "Booking",
        back_populates="student",
        foreign_keys="Booking.student_id",
        cascade="all, delete-orphan"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    course_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default="Active", nullable=False)

    examinations = db.relationship(
        "Examination",
        back_populates="course",
        cascade="all, delete-orphan"
    )


class Examination(db.Model):
    __tablename__ = "examinations"

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey("courses.id"), nullable=False)
    examiner_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    name = db.Column(db.String(150), nullable=False)
    examination_type = db.Column(db.String(30), nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    maximum_marks = db.Column(db.Float, nullable=False)
    slot_creation_start = db.Column(db.DateTime)
    slot_creation_end = db.Column(db.DateTime)
    slot_booking_start = db.Column(db.DateTime)
    slot_booking_end = db.Column(db.DateTime)
    status = db.Column(db.String(20), default="Draft", nullable=False)

    course = db.relationship("Course", back_populates="examinations")
    assigned_examiner = db.relationship(
        "User",
        back_populates="examinations",
        foreign_keys=[examiner_id]
    )
    rubrics = db.relationship(
        "ExaminationRubric",
        back_populates="examination",
        cascade="all, delete-orphan"
    )
    slots = db.relationship(
        "ExaminationSlot",
        back_populates="examination",
        cascade="all, delete-orphan"
    )


class ExaminationRubric(db.Model):
    __tablename__ = "examination_rubrics"

    id = db.Column(db.Integer, primary_key=True)
    examination_id = db.Column(db.Integer, db.ForeignKey("examinations.id"), nullable=False)
    criterion_name = db.Column(db.String(150), nullable=False)
    maximum_marks = db.Column(db.Float, nullable=False)
    weightage = db.Column(db.Float)
    description = db.Column(db.Text)

    examination = db.relationship("Examination", back_populates="rubrics")
    evaluations = db.relationship(
        "Evaluation",
        back_populates="rubric",
        cascade="all, delete-orphan"
    )


class ExaminationSlot(db.Model):
    __tablename__ = "examination_slots"

    id = db.Column(db.Integer, primary_key=True)
    examination_id = db.Column(db.Integer, db.ForeignKey("examinations.id"), nullable=False)
    examiner_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    maximum_student_capacity = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="Available", nullable=False)

    examination = db.relationship("Examination", back_populates="slots")
    examiner = db.relationship("User", back_populates="slots")
    bookings = db.relationship(
        "Booking",
        back_populates="slot",
        cascade="all, delete-orphan"
    )


class Booking(db.Model):
    __tablename__ = "bookings"
    __table_args__ = (
        db.UniqueConstraint("student_id", "slot_id", name="uq_student_slot"),
    )

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey("examination_slots.id"), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default="Booked", nullable=False)
    final_marks = db.Column(db.Float)
    feedback = db.Column(db.Text)

    student = db.relationship(
        "User",
        back_populates="bookings",
        foreign_keys=[student_id]
    )
    slot = db.relationship("ExaminationSlot", back_populates="bookings")
    evaluations = db.relationship(
        "Evaluation",
        back_populates="booking",
        cascade="all, delete-orphan"
    )


class Evaluation(db.Model):
    __tablename__ = "evaluations"
    __table_args__ = (
        db.UniqueConstraint("booking_id", "rubric_id", name="uq_booking_rubric"),
    )

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id"), nullable=False)
    rubric_id = db.Column(db.Integer, db.ForeignKey("examination_rubrics.id"), nullable=False)
    marks = db.Column(db.Float, nullable=False)
    remarks = db.Column(db.Text)

    booking = db.relationship("Booking", back_populates="evaluations")
    rubric = db.relationship("ExaminationRubric", back_populates="evaluations")


class ExaminerProfile(db.Model):
    __tablename__ = "examiner_profiles"

    id = db.Column(db.Integer, primary_key=True)
    examiner_id = db.Column(db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    contact_details = db.Column(db.String(255))
    department = db.Column(db.String(120))
    status = db.Column(db.String(20), default="Pending", nullable=False)

    user = db.relationship("User", back_populates="examiner_profile")