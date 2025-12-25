from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.complience_event import ComplianceEvent
from app.schemas.complience_event import ComplianceEventCreate, ComplianceEventResponse

router = APIRouter(prefix="/events", tags=["Compliance Events"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=ComplianceEventResponse)
def create_event(
    event: ComplianceEventCreate,
    db: Session = Depends(get_db)
):
    new_event = ComplianceEvent(**event.dict())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event
