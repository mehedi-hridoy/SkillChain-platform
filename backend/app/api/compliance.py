from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.dependencies import get_db, get_current_user, require_role
from app.models.complience_event import ComplianceEvent
from app.models.user import User
from app.services.file_upload import FileUploadService
from typing import Optional, List
from datetime import date, datetime

router = APIRouter(prefix="/compliance", tags=["Compliance Management"])

# Schemas
class ComplianceEventCreate(BaseModel):
    event_type: str  # FIRE_SAFETY_CHECK, PPE_INSPECTION, BUILDING_AUDIT, CHEMICAL_TEST, WORKER_TRAINING
    status: str  # PASS, FAIL, PENDING, ATTENTION_REQUIRED
    area: str  # e.g., "Cutting Section - Floor 3"
    evidence_type: Optional[str] = None  # CERTIFICATE, TEST_REPORT, PHOTO, AUDIT_REPORT, TRAINING_RECORD
    expiry_date: Optional[date] = None
    notes: Optional[str] = None
    batch_id: Optional[int] = None

class ComplianceEventResponse(BaseModel):
    id: int
    factory_id: int
    user_id: int
    event_type: str
    status: str
    area: str
    evidence_type: Optional[str]
    expiry_date: Optional[date]
    notes: Optional[str]
    document_urls: Optional[List[str]]
    approved_by: Optional[int]
    approved_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.post("/events", response_model=ComplianceEventResponse)
async def create_compliance_event(
    event: ComplianceEventCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new compliance event
    Workers, Managers, Factory Admins can create events
    """
    if not current_user.factory_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must be associated with a factory"
        )
    
    compliance_event = ComplianceEvent(
        factory_id=current_user.factory_id,
        user_id=current_user.id,
        event_type=event.event_type,
        status=event.status,
        area=event.area,
        evidence_type=event.evidence_type,
        expiry_date=event.expiry_date,
        notes=event.notes,
        batch_id=event.batch_id,
        document_urls=[]  # Documents added separately
    )
    
    db.add(compliance_event)
    db.commit()
    db.refresh(compliance_event)
    
    return compliance_event

@router.post("/events/{event_id}/upload-document")
async def upload_compliance_document(
    event_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload and attach document to compliance event
    """
    event = db.query(ComplianceEvent).filter(ComplianceEvent.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    
    # Check permission
    if event.factory_id != current_user.factory_id and current_user.role != "platform_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    # Upload file
    try:
        file_info = await FileUploadService.save_file(file, category="compliance")
        
        # Add to document_urls
        if event.document_urls is None:
            event.document_urls = []
        
        event.document_urls.append(file_info["url"])
        db.commit()
        
        return {
            "success": True,
            "message": "Document uploaded and attached",
            "file": file_info,
            "event_id": event_id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}"
        )

@router.get("/events", response_model=List[ComplianceEventResponse])
def list_compliance_events(
    factory_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    event_type: Optional[str] = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List compliance events
    - Users see events from their factory
    - Platform admin sees all events
    """
    query = db.query(ComplianceEvent)
    
    # Apply filters based on role
    if current_user.role != "platform_admin":
        if not current_user.factory_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not associated with a factory"
            )
        query = query.filter(ComplianceEvent.factory_id == current_user.factory_id)
    elif factory_id:
        query = query.filter(ComplianceEvent.factory_id == factory_id)
    
    # Additional filters
    if status_filter:
        query = query.filter(ComplianceEvent.status == status_filter)
    if event_type:
        query = query.filter(ComplianceEvent.event_type == event_type)
    
    events = query.order_by(ComplianceEvent.created_at.desc()).limit(limit).all()
    return events

@router.get("/events/{event_id}", response_model=ComplianceEventResponse)
def get_compliance_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get single compliance event details
    """
    event = db.query(ComplianceEvent).filter(ComplianceEvent.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    
    # Check permission
    if event.factory_id != current_user.factory_id and current_user.role != "platform_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    return event

@router.put("/events/{event_id}/approve")
def approve_compliance_event(
    event_id: int,
    current_user: User = Depends(require_role(["manager", "factory_admin", "platform_admin"])),
    db: Session = Depends(get_db)
):
    """
    Approve a compliance event
    Only managers, factory admins, and platform admins can approve
    """
    event = db.query(ComplianceEvent).filter(ComplianceEvent.id == event_id).first()
    
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found")
    
    # Check permission
    if event.factory_id != current_user.factory_id and current_user.role != "platform_admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    event.approved_by = current_user.id
    event.approved_at = datetime.now()
    
    db.commit()
    
    return {"success": True, "message": "Event approved", "event_id": event_id}

@router.get("/stats")
def get_compliance_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get compliance statistics for factory dashboard
    """
    factory_id = current_user.factory_id
    
    if not factory_id and current_user.role != "platform_admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User not associated with a factory"
        )
    
    query = db.query(ComplianceEvent)
    if factory_id:
        query = query.filter(ComplianceEvent.factory_id == factory_id)
    
    total_events = query.count()
    passed_events = query.filter(ComplianceEvent.status == "PASS").count()
    failed_events = query.filter(ComplianceEvent.status == "FAIL").count()
    pending_events = query.filter(ComplianceEvent.status == "PENDING").count()
    
    compliance_score = int((passed_events / total_events * 100)) if total_events > 0 else 0
    
    return {
        "total_events": total_events,
        "passed": passed_events,
        "failed": failed_events,
        "pending": pending_events,
        "compliance_score": compliance_score
    }
