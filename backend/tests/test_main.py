import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import shutil
import time

from database import Base, get_db
import database
from main import app
import utils

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
database.SessionLocal = TestingSessionLocal
database.engine = engine

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    os.makedirs(utils.CERTIFICATE_DIR, exist_ok=True)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists(utils.CERTIFICATE_DIR):
        try:
            shutil.rmtree(utils.CERTIFICATE_DIR)
        except Exception:
            pass
    engine.dispose()
    if os.path.exists("test.db"):
        try:
            os.remove("test.db")
        except Exception:
            pass

def test_create_job():
    response = client.post("/jobs/", json={
        "recipients": [
            {"recipient_name": "Alice", "email": "alice@example.com", "course_name": "Python 101"},
            {"recipient_name": "Bob", "email": "bob@example.com", "course_name": "Python 101"}
        ]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "pending"
    assert len(data["certificates"]) == 2
    
def test_create_job_empty():
    response = client.post("/jobs/", json={
        "recipients": []
    })
    assert response.status_code == 400

def test_job_processing_and_status():
    response = client.post("/jobs/", json={
        "recipients": [
            {"recipient_name": "Charlie", "email": "charlie@example.com", "course_name": "Go 101"},
            {"recipient_name": "David", "email": "david@example.com", "course_name": "Go 101"}
        ]
    })
    job_id = response.json()["id"]
    
    time.sleep(1.5)
    
    status_response = client.get(f"/jobs/{job_id}/status")
    assert status_response.status_code == 200
    data = status_response.json()
    assert data["status"] == "completed"
    assert data["total_certificates"] == 2
    assert data["generated"] == 2
    assert data["failed"] == 0

def test_job_processing_with_failure():
    response = client.post("/jobs/", json={
        "recipients": [
            {"recipient_name": "Eve", "email": "eve@example.com", "course_name": "Rust 101"},
            {"recipient_name": "FAIL_USER", "email": "fail@example.com", "course_name": "Rust 101"}
        ]
    })
    job_id = response.json()["id"]
    
    time.sleep(1.5)
    
    status_response = client.get(f"/jobs/{job_id}/status")
    data = status_response.json()
    assert data["status"] == "completed_with_errors"
    assert data["generated"] == 1
    assert data["failed"] == 1

def test_download_certificate():
    response = client.post("/jobs/", json={
        "recipients": [
            {"recipient_name": "Frank", "email": "frank@example.com", "course_name": "C++ 101"}
        ]
    })
    job_id = response.json()["id"]
    
    time.sleep(1.5)
    
    job_response = client.get(f"/jobs/{job_id}")
    cert_id = job_response.json()["certificates"][0]["id"]
    
    dl_response = client.get(f"/certificates/{cert_id}/download")
    assert dl_response.status_code == 200
    assert dl_response.headers["content-type"] == "image/jpeg"

