from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
import pandas as pd
import io
from sqlalchemy.orm import Session
import models, schemas, database, utils
import os

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Bulk Certificate Generator")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def process_job(job_id: int, db: Session):
    job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not job:
        return
    
    job.status = "processing"
    db.commit()

    all_success = True
    for cert in job.certificates:
        cert.status = "processing"
        db.commit()
        
        try:
            filepath = utils.generate_certificate(cert.recipient_name, cert.course_name)
            cert.file_path = filepath
            cert.status = "generated"
        except Exception as e:
            cert.status = "failed"
            cert.error_message = str(e)
            all_success = False
        
        db.commit()

    job.status = "completed" if all_success else "completed_with_errors"
    db.commit()

@app.post("/jobs/", response_model=schemas.JobResponse)
def create_job(job_req: schemas.JobCreate, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    if not job_req.recipients:
        raise HTTPException(status_code=400, detail="Recipients list cannot be empty")
        
    db_job = models.Job(status="pending")
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    
    for recipient in job_req.recipients:
        db_cert = models.Certificate(
            job_id=db_job.id,
            recipient_name=recipient.recipient_name,
            email=recipient.email,
            course_name=recipient.course_name,
            status="pending"
        )
        db.add(db_cert)
        
    db.commit()
    db.refresh(db_job)
    
    background_tasks.add_task(run_job_background, db_job.id)
    return db_job

@app.post("/jobs/upload/", response_model=schemas.JobResponse)
async def upload_job(background_tasks: BackgroundTasks, file: UploadFile = File(...), db: Session = Depends(database.get_db)):
    content = await file.read()
    
    recipients = []
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(content))
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Only CSV and Excel files are supported")
            
        # Normalize columns: lower case, stripped, replace spaces with underscores
        df.columns = [str(c).lower().strip().replace(' ', '_') for c in df.columns]
        
        # Flexible column mapping
        name_col, email_col, course_col = None, None, None
        for col in df.columns:
            if not name_col and any(k in col for k in ['name', 'recipient', 'student']):
                name_col = col
            if not email_col and any(k in col for k in ['email', 'e-mail', 'mail']):
                email_col = col
            if not course_col and any(k in col for k in ['course', 'program', 'class', 'certificate', 'event']):
                course_col = col
                
        if not (name_col and email_col and course_col):
            raise HTTPException(
                status_code=400, 
                detail="Could not auto-detect columns. Please ensure your file has columns that resemble 'Name', 'Email', and 'Course'."
            )
            
        for _, row in df.iterrows():
            name = row.get(name_col)
            email = row.get(email_col)
            course = row.get(course_col)
            
            if pd.notna(name) and pd.notna(email) and pd.notna(course):
                recipients.append(schemas.RecipientCreate(
                    recipient_name=str(name).strip(), 
                    email=str(email).strip(), 
                    course_name=str(course).strip()
                ))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error parsing file: {str(e)}")
        
    if not recipients:
        raise HTTPException(status_code=400, detail="No valid recipients found in the file.")
        
    job_req = schemas.JobCreate(recipients=recipients)
    return create_job(job_req, background_tasks, db)

def run_job_background(job_id: int):
    db = database.SessionLocal()
    try:
        process_job(job_id, db)
    finally:
        db.close()

@app.get("/jobs/{job_id}", response_model=schemas.JobResponse)
def get_job(job_id: int, db: Session = Depends(database.get_db)):
    db_job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
    return db_job

@app.get("/jobs/{job_id}/status", response_model=schemas.JobStatusResponse)
def get_job_status(job_id: int, db: Session = Depends(database.get_db)):
    db_job = db.query(models.Job).filter(models.Job.id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=404, detail="Job not found")
        
    total = len(db_job.certificates)
    generated = sum(1 for c in db_job.certificates if c.status == "generated")
    failed = sum(1 for c in db_job.certificates if c.status == "failed")
    pending = sum(1 for c in db_job.certificates if c.status in ["pending", "processing"])
    
    return schemas.JobStatusResponse(
        id=db_job.id,
        status=db_job.status,
        total_certificates=total,
        generated=generated,
        failed=failed,
        pending=pending
    )

@app.get("/certificates/{certificate_id}/download")
def download_certificate(certificate_id: int, db: Session = Depends(database.get_db)):
    cert = db.query(models.Certificate).filter(models.Certificate.id == certificate_id).first()
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    if cert.status != "generated" or not cert.file_path:
        raise HTTPException(status_code=400, detail="Certificate is not available for download")
    if not os.path.exists(cert.file_path):
        raise HTTPException(status_code=404, detail="File not found on server")
        
    return FileResponse(cert.file_path, media_type="image/jpeg", filename=f"certificate_{cert.recipient_name.replace(' ', '_')}.jpg")
