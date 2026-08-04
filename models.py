# from sqlalchemy import Column,Integer,String
# from database import Base 
# from sqlalchemy import Column, Integer, String, ForeignKey
# from sqlalchemy.orm import relationship

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer,primary_key=True,index=True)

#     email = Column(String,unique=True,index=True)

#     hashed_password = Column(String)




from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    uploaded_files = relationship("UploadedFile", back_populates="owner")
    analysis_runs = relationship("AnalysisRun", back_populates="owner")

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    path = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey('users.id'))

    owner = relationship("User", back_populates="uploaded_files")

class AnalysisRun(Base):
    __tablename__ = "analysis_runs"

    id = Column(Integer, primary_key=True, index=True)
    job_description = Column(Text)
    skills = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)

    owner = relationship("User", back_populates="analysis_runs")
    results = relationship("AnalysisResult", back_populates="run",
                            cascade="all, delete-orphan", order_by="AnalysisResult.id")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey('analysis_runs.id'), nullable=False)
    candidate_name = Column(String)
    match_score = Column(Integer)
    shortlisted = Column(Boolean)
    highlights = Column(Text)
    risk_factor = Column(Text)

    run = relationship("AnalysisRun", back_populates="results")








