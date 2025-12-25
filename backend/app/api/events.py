from typing import List, Optional
from fastapi import APIRouter, Depends, Query
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


@router.get("/", response_model=List[ComplianceEventResponse])
def list_events(
    factory_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    event_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(ComplianceEvent)

    if factory_id:
        query = query.filter(ComplianceEvent.factory_id == factory_id)

    if user_id:
        query = query.filter(ComplianceEvent.user_id == user_id)

    if event_type:
        query = query.filter(ComplianceEvent.event_type == event_type)

    return query.order_by(ComplianceEvent.created_at.desc()).all()


@router.get("/summary")
def compliance_summary(
    factory_id: int,
    db: Session = Depends(get_db)
):
    total = db.query(ComplianceEvent)\
        .filter(ComplianceEvent.factory_id == factory_id)\
        .count()

    compliant = db.query(ComplianceEvent)\
        .filter(
            ComplianceEvent.factory_id == factory_id,
            ComplianceEvent.status == "COMPLIANT"
        ).count()

    return {
        "factory_id": factory_id,
        "total_events": total,
        "compliant_events": compliant,
        "compliance_rate": (compliant / total * 100) if total > 0 else 0
    }
