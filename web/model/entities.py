from sqlalchemy import Column, Integer, String, Sequence, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import connector
from datetime import datetime
from model import entities
from flask_login import UserMixin

class User(connector.Manager.Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    username = Column(String(20))
    email = Column(String(120))
    password = Column(String(12))
    name = Column(String(20))
    fullname = Column(String(50))
    #posts = relationship('Post', backref='username', lazy=True)

class Post(connector.Manager.Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    date_posted = Column(DateTime, nullable=False, default=datetime.utcnow)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    rel_username = relationship(User, foreign_keys=[user_id])
