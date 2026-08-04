from sqlalchemy.orm import Session
import models, schemas, crud, database
from fastapi import FastAPI, HTTPException, Depends , File , UploadFile , Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Security
from typing import List
from schemas import JobDescription, Skills, UploadFileResponse
import shutil
import os
from langchain_backend import process_with_langchain
from fastapi.responses import FileResponse
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY")

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

###################################### for the access tokens ##############################
def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

bearer_scheme = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(bearer_scheme),
    db: Session = Depends(database.get_db),
) -> models.User:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Session expired, please log in again")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user = crud.get_user_by_email(db, email=email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

#####################################  API for sign up ###################################
@app.post("/signup/", response_model=schemas.User)
def signup(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered.")
    return crud.create_user(db=db, user=user)

#################################### API for log in #######################################
@app.post("/login/")
def login(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if not db_user or not crud.verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    token_expires = datetime.timedelta(hours=1)
    token = create_access_token(data={"sub": db_user.email}, expires_delta=token_expires)
    
    return {"token": token}


################################### API for uploading PDFs(links) ############################### 

@app.post('/upload', response_model=schemas.UploadedFile)
def upload_file(uploaded_file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    os.makedirs('files', exist_ok=True)
    path = f"files/{uploaded_file.filename}"
    with open(path, 'wb') as file:
        shutil.copyfileobj(uploaded_file.file, file)

    file_data = schemas.UploadedFile(filename=uploaded_file.filename, path=path)
    db_file = crud.create_uploaded_file(db=db, file=file_data)

    return db_file

################################### API to get the pdf links  ################################
@app.get('/files/{filename}', response_class=FileResponse)
def get_file(filename: str):
    file_path = os.path.join('files', filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="File not found")

#################################### API  for langchain response part #########################
@app.post("/process_text", response_model=schemas.AnalysisRunOut)
async def process_text(
    job_description: str = Form(...),
    skills: str = Form(...),
    files: List[UploadFile] = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="You can upload up to 10 files only")

    file_bytes = [await file.read() for file in files]
    candidates = process_with_langchain(job_description, skills, file_bytes)
    return crud.create_analysis_run(
        db, owner_id=current_user.id, job_description=job_description, skills=skills, candidates=candidates
    )

#################################### API for past shortlisting runs ###########################
@app.get("/history", response_model=List[schemas.AnalysisRunOut])
def get_history(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(database.get_db),
):
    return crud.get_analysis_runs_by_owner(db, owner_id=current_user.id)
