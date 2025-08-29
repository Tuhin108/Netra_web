from sqlalchemy import create_engine, Column, String, Integer, Float, Text, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///scan_results.db')

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ScanResult(Base):
    __tablename__ = "scan_results"

    scan_id = Column(String, primary_key=True, index=True)
    url = Column(String, nullable=False)
    status = Column(String, default="processing")
    progress = Column(Float, default=0.0)
    message = Column(String, default="Starting scan...")
    trace_result = Column(JSON, nullable=True)
    verdict = Column(JSON, nullable=True)
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_update = Column(DateTime, default=datetime.datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)
