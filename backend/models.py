from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
import datetime
from database import Base

class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, default="pending")  # pending, processing, completed, completed_with_errors
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    certificates = relationship("Certificate", back_populates="job")

class Certificate(Base):
    __tablename__ = "certificates"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    recipient_name = Column(String, index=True)
    email = Column(String, index=True)
    course_name = Column(String)
    status = Column(String, default="pending")  # pending, generated, failed
    error_message = Column(String, nullable=True)
    file_path = Column(String, nullable=True)

    job = relationship("Job", back_populates="certificates")
