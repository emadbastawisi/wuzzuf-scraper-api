from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel, EmailStr
from sqlalchemy import LargeBinary


# user section

class UserPersonalInfo(BaseModel):
    middel_name: Optional[str]
    birthdate: date
    gender: str
    nationality: str
    marital_status:  Optional[str]
    military_status: Optional[str]
    driving_license: Optional[str]
    address: str
    phone: str


class UserCareerInterests(BaseModel):
    career_level: str
    job_types: str
    job_titels: str
    job_categories: str
    min_salary: str
    hide_min_salary: Optional[bool]
    perfered_job_location: Optional[str]
    current_job_search_status: Optional[str]


class UserCv(BaseModel):
    cv_name: str
    cv_file: LargeBinary

    class Config():
        arbitrary_types_allowed = True


class UserImg(BaseModel):
    img_name: str
    img_file: LargeBinary

    class Config():
        arbitrary_types_allowed = True


class User(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr


class UserCreateIn(User):
    password: str
    pass


class UserCreateOut(User):
    created_at: datetime

    class Config():
        from_attributes = True


class UserOut(User):
    created_at: datetime
    img: Optional[UserImg]
    cv: Optional[UserCv]
    personal_info: Optional[UserPersonalInfo]
    career_interests: Optional[UserCareerInterests]

    class Config():
        from_attributes = True


class CurrentUserOut(User):
    img: Optional[UserImg]

    class Config():
        from_attributes = True

# auth section


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int


class LoginOut(Token):
    current_user: CurrentUserOut

    class Config():
        from_attributes = True


# job section
class Job(BaseModel):
    title: str
    company: str
    location: str
    type: str
    skills: str
    link: str


class JobCreate(Job):
    created_at: datetime
    expired_at: datetime


class JobOut(Job):
    created_at: datetime

    class Config():
        from_attributes = True

# keywords section


class keywords(BaseModel):
    keywords: str


class Out_Search_Keyword(BaseModel):
    user_id: int
    id: int
    keywords: str


class Url(BaseModel):
    url: str


class Password(BaseModel):
    password: str
