from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base

class ComplianceEvent(Base):
    __tablename__ = "compliance_events"

    id = Column(Integer, primary_key=True, index=True)

    factory_id = Column(Integer, ForeignKey("factories.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    event_type = Column(String, nullable=False)  
    # e.g. FIRE_EXIT_CHECK, PPE_CHECK

    status = Column(String, nullable=False)  
    # COMPLIANT / NON_COMPLIANT

    area = Column(String, nullable=False)  
    # Line 3, Floor 2, Exit Gate A

    evidence_url = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
