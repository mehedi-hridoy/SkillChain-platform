from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON, Date
from sqlalchemy.sql import func
from app.db.base import Base

class ComplianceEvent(Base):
    __tablename__ = "compliance_events"

    id = Column(Integer, primary_key=True, index=True)

    factory_id = Column(Integer, ForeignKey("factories.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    event_type = Column(String, nullable=False)  
    # e.g. FIRE_SAFETY_CHECK, PPE_INSPECTION, BUILDING_AUDIT, CHEMICAL_TEST, WORKER_TRAINING

    status = Column(String, nullable=False)  
    # PASS / FAIL / PENDING / ATTENTION_REQUIRED

    area = Column(String, nullable=False)  
    # e.g. "Cutting Section - Floor 3", "Sewing Line 5", "Warehouse B"

    evidence_url = Column(String, nullable=True)  # Legacy field for backward compatibility
    
    # NEW: Store multiple document URLs as JSON array
    document_urls = Column(JSON, nullable=True)  
    # e.g. ["/files/compliance/cert1.pdf", "/files/compliance/photo1.jpg"]
    
    # NEW: Document/evidence type classification
    evidence_type = Column(String, nullable=True)  
    # e.g. CERTIFICATE, TEST_REPORT, PHOTO, AUDIT_REPORT, TRAINING_RECORD
    
    # NEW: Certificate expiry tracking
    expiry_date = Column(Date, nullable=True)
    
    # NEW: Approval tracking
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Additional notes/description
    notes = Column(String, nullable=True)
    
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
