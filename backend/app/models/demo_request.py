from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class DemoRequest(Base):
    """
    Companies/individuals requesting demo/registration
    Admin approves and creates accounts
    """
    __tablename__ = "demo_requests"

    id = Column(Integer, primary_key=True, index=True)
    
    # Company Information
    company_name = Column(String, nullable=False)
    industry = Column(String, nullable=True)  # RMG, Textile, etc.
    company_size = Column(String, nullable=True)  # 1-50, 51-200, 201-500, 500+
    
    # Contact Person
    contact_name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)  # Store hashed password
    
    # Request Details
    role_requested = Column(String, nullable=False)  # factory_admin, manager, etc.
    message = Column(Text, nullable=True)
    
    # Status
    status = Column(String, default="pending")  # pending, approved, rejected
    
    # Admin Actions
    reviewed_by = Column(Integer, nullable=True)  # User ID of admin who reviewed
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    admin_notes = Column(Text, nullable=True)
    
    # Created user (after approval)
    user_id = Column(Integer, nullable=True)  # Link to created user account
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
