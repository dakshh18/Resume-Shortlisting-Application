# from sqlalchemy import Column,Integer,String
# from database import Base 
# from sqlalchemy import Column, Integer, String, ForeignKey
# from sqlalchemy.orm import relationship

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer,primary_key=True,index=True)

#     email = Column(String,unique=True,index=True)

#     hashed_password = Column(String)




from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    uploaded_files = relationship("UploadedFile", back_populates="owner")

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    path = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship("User", back_populates="uploaded_files")








