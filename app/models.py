from .database import Base
from sqlalchemy import TIMESTAMP, Column, Integer, String, text , ForeignKey
from sqlalchemy.orm import relationship


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, nullable=False )
    title = Column(String , nullable=False)
    company = Column(String , nullable=False)
    location = Column(String , nullable=False)
    type = Column(String , nullable=False)
    skills = Column(String , nullable=False)
    link = Column(String , nullable=False)
    created_at = Column(TIMESTAMP , nullable=False )
    expired_at = Column(TIMESTAMP , nullable=False, server_default=text("(created_at + interval '7 days')"))

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False )
    username = Column(String , nullable=False , unique=True)
    email = Column(String , nullable=False , unique=True)
    password = Column(String , nullable=False)
    created_at = Column(TIMESTAMP(timezone=True) , nullable=False , server_default=text('now()'))    

class User_Keyword(Base):
    __tablename__ = "user_keywords"
    id = Column(Integer, primary_key=True, nullable=False )
    user_id = Column(Integer, ForeignKey('users.id' , ondelete='cascade'), nullable=False )
    keywords = Column(String , nullable=True)

# class Search_Keyword_Result(Base):
#     __tablename__ = "search_keyword_results"
#     search_keyword = Column(Integer,primary_key=True, nullable=False )
#     search_keyword_result = Column(Integer, nullable=False )
#     created_at = Column(TIMESTAMP(timezone=True) , nullable=False , server_default=text('now()'))



