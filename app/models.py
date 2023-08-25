from .database import Base
from sqlalchemy import TIMESTAMP, Boolean, Column, Date, Integer, LargeBinary, String, text, ForeignKey
from sqlalchemy.orm import relationship


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    company = Column(String, nullable=False)
    location = Column(String, nullable=False)
    type = Column(String, nullable=False)
    skills = Column(String, nullable=False)
    link = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)
    expired_at = Column(TIMESTAMP, nullable=False, server_default=text(
        "(created_at + interval '7 days')"))


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=False),
                        nullable=False, server_default=text('now()'))
    cv = relationship("User_Cv", uselist=False)
    img = relationship("User_Img", uselist=False)
    personal_info = relationship("User_Personal_Info", uselist=False)
    career_interests = relationship("User_Career_Interests", uselist=False)


class User_Personal_Info(Base):
    __tablename__ = "users_personal_info"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey(
        'users.id', ondelete='cascade'), nullable=False, unique=True)
    middel_name = Column(String, nullable=True)
    birthdate = Column(Date, nullable=False)
    gender = Column(String, nullable=False)
    nationality = Column(String, nullable=False)
    marital_status = Column(String, nullable=True)
    military_status = Column(String, nullable=True)
    driving_license = Column(String, nullable=True)
    address = Column(String, nullable=False)
    phone = Column(String, nullable=False)


class User_Career_Interests(Base):
    __tablename__ = "users_career_interests"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey(
        'users.id', ondelete='cascade'), nullable=False, unique=True)
    career_level = Column(String, nullable=False)
    job_types = Column(String, nullable=False)
    job_titels = Column(String, nullable=False)
    job_categories = Column(String, nullable=False)
    min_salary = Column(String, nullable=False)
    hide_min_salary = Column(Boolean, nullable=False, default=False)
    perfered_job_location = Column(String, nullable=True)
    current_job_search_status = Column(String, nullable=True)


class User_Cv(Base):
    __tablename__ = "users_cv"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey(
        'users.id', ondelete='cascade'), nullable=False, unique=True)
    cv_name = Column(String, nullable=False)
    cv_file = Column(LargeBinary, nullable=False)


class User_Img(Base):
    __tablename__ = "users_img"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey(
        'users.id', ondelete='cascade'), nullable=False, unique=True)
    img_name = Column(String, nullable=False)
    img_file = Column(LargeBinary, nullable=False)


class User_Keyword(Base):
    __tablename__ = "user_keywords"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey(
        'users.id', ondelete='cascade'), nullable=False, unique=True)
    keywords = Column(String, nullable=True)
