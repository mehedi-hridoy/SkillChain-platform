from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.product import Product

router = APIRouter(prefix="/products", tags=["Products"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/")
def create_product(product: dict, db: Session = Depends(get_db)):
    obj = Product(**product)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
