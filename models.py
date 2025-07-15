from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker,relationship
from sqlalchemy import Column, Integer, String,ForeignKey,Boolean

engine = create_engine("sqlite:///database.db", echo=False)
Base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer,primary_key=True,index=True)
    user_id = Column(String,unique=True)
    user_name = Column(String)

    wishlist = relationship("WishLists",back_populates="user")
class WishLists(Base):
    __tablename__ = 'wishlists'
    id = Column(Integer,primary_key=True,index=True)
    title = Column(String)
    description = Column(String)
    check_mark = Column(Boolean) # True - checked, False - unchecked

    user_id = Column(String,ForeignKey('users.user_id'))

    user = relationship("User",back_populates="wishlist")
Base.metadata.create_all(bind=engine)
