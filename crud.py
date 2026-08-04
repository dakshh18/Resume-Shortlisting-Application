from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

####

def create_uploaded_file(db: Session, file: schemas.UploadedFile):
    db_file = models.UploadedFile(filename=file.filename, path=file.path)
    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

####

def create_analysis_run(db: Session, owner_id: int, job_description: str, skills: str, candidates: list):
    db_run = models.AnalysisRun(job_description=job_description, skills=skills, owner_id=owner_id)
    db_run.results = [
        models.AnalysisResult(
            candidate_name=c.candidate_name,
            match_score=c.match_score,
            shortlisted=c.shortlisted,
            highlights=c.highlights,
            risk_factor=c.risk_factor,
        )
        for c in candidates
    ]
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    return db_run

def get_analysis_runs_by_owner(db: Session, owner_id: int):
    return (
        db.query(models.AnalysisRun)
        .filter(models.AnalysisRun.owner_id == owner_id)
        .order_by(models.AnalysisRun.created_at.desc())
        .all()
    )

