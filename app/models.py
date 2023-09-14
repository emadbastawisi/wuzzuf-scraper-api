from datetime import timedelta
from .database import Base
from sqlalchemy import TIMESTAMP, Boolean, Column, DateTime, Integer, LargeBinary, String, text, ForeignKey, event
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.types import TypeDecorator, String


class ListOfString(TypeDecorator):
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return ','.join(value)

    def process_result_value(self, value, dialect):
        if value is not None:
            return value.split(',')


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
    expired_at = Column(TIMESTAMP, nullable=False)


@event.listens_for(Job, 'before_insert')
def set_expired_at(mapper, connection, target):
    target.expired_at = target.created_at + timedelta(days=7)


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
    work_experience = relationship("User_Work_Experience", uselist=True)
    skills = relationship("User_Skills", uselist=True)
    languages = relationship("User_Language", uselist=True)
    highschool = relationship("User_HighSchool", uselist=False)
    degrees = relationship("User_Degree", uselist=True)


class User_Personal_Info(Base):
    __tablename__ = "users_personal_info"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey(
        'users.id', ondelete='cascade'), nullable=False, unique=True)
    middel_name = Column(String, nullable=True)
    birthdate = Column(DateTime, nullable=False)
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
    years_of_experience = Column(String, nullable=True)
    job_types = Column(ListOfString, nullable=False)
    job_titles = Column(ListOfString, nullable=True)
    job_categories = Column(ListOfString, nullable=False)
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
    updated_at = Column(TIMESTAMP(timezone=False),
                        nullable=False, server_default=text('now()'))


class User_Img(Base):
    __tablename__ = "users_img"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey(
        'users.id', ondelete='cascade'), nullable=False, unique=True)
    img_name = Column(String, nullable=False)
    img_file = Column(LargeBinary, nullable=False)


class User_Work_Experience(Base):
    __tablename__ = "users_work_experience"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey(
        'users.id', ondelete='cascade'), nullable=False)
    experience_type = Column(String, nullable=False)
    job_title = Column(String, nullable=False)
    job_category = Column(ListOfString, nullable=False)
    company_name = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=True)
    work_there = Column(Boolean, nullable=False, default=False)
    updated_at = Column(TIMESTAMP(timezone=False),
                        nullable=False, server_default=text('now()'))


class User_Degree(Base):
    __tablename__ = "users_degrees"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey(
        'users.id', ondelete='cascade'), nullable=False)
    degree = Column(String, nullable=False)
    field_of_study = Column(ListOfString, nullable=False)
    university = Column(String, nullable=False)
    degree_year = Column(String, nullable=False)
    grade = Column(String, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=False),
                        nullable=False, server_default=text('now()'))


class User_HighSchool(Base):
    __tablename__ = "users_highschools"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey(
        'users.id', ondelete='cascade'), nullable=False)
    degree = Column(String, nullable=False)
    school_name = Column(String, nullable=False)
    certificate_name = Column(String, nullable=False)
    language_of_study = Column(String, nullable=False)
    degree_year = Column(String, nullable=False)
    grade = Column(String, nullable=True)
    updated_at = Column(TIMESTAMP(timezone=False),
                        nullable=False, server_default=text('now()'))


class User_Skills(Base):
    __tablename__ = "users_skills"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey(
        'users.id', ondelete='cascade'), nullable=False)
    skill = Column(String, nullable=False)
    proficiency = Column(String, nullable=False)


class User_Language(Base):
    __tablename__ = "users_languages"
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(Integer, ForeignKey(
        'users.id', ondelete='cascade'), nullable=False)
    language = Column(String, nullable=False)
    proficiency = Column(String, nullable=False)


class Skills(Base):
    __tablename__ = "skills"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    frequency = Column(Integer, nullable=False)


# class User_Keyword(Base):
#     __tablename__ = "user_keywords"
#     id = Column(Integer, primary_key=True, nullable=False)
#     user_id = Column(Integer, ForeignKey(
#         'users.id', ondelete='cascade'), nullable=False, unique=True)
#     keywords = Column(String, nullable=True)
