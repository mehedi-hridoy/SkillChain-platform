from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.batch import Batch

router = APIRouter(prefix="/batches", tags=["Batches"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_batch(batch: dict, db: Session = Depends(get_db)):
    obj = Batch(**batch)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
