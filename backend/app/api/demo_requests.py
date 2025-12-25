from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from app.core.dependencies import get_db, get_current_user, require_role
from app.models.demo_request import DemoRequest
from app.models.user import User
from app.models.factory import Factory
from app.core.security import get_password_hash
from app.core.roles import normalize_role, FACTORY_ROLES
import bcrypt
from datetime import datetime
from typing import Optional, List

router = APIRouter(prefix="/demo-request", tags=["Demo Requests"])

# Schemas
class DemoRequestCreate(BaseModel):
    company_name: str
    industry: Optional[str] = "RMG"
    company_size: Optional[str] = None
    contact_name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    role_requested: str
    message: Optional[str] = None

class DemoRequestResponse(BaseModel):
    id: int
    company_name: str
    contact_name: str
    email: str
    phone: Optional[str]
    role_requested: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Public endpoint - anyone can submit demo request
@router.post("/submit", response_model=DemoRequestResponse, status_code=status.HTTP_201_CREATED)
def submit_demo_request(request: DemoRequestCreate, db: Session = Depends(get_db)):
    """
    Public endpoint for companies to request demo/registration
    No authentication required
    """
    # Check if email already exists in demo requests
    existing_request = db.query(DemoRequest).filter(
        DemoRequest.email == request.email,
        DemoRequest.status == "pending"
    ).first()
    
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A demo request with this email is already pending"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists. Please login instead."
        )
    
    # Normalize role from frontend to backend format
    normalized_role = normalize_role(request.role_requested)
    
    # Validate role
    valid_roles = ["factory_admin", "manager", "buyer", "platform_admin"]
    if normalized_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Hash password
    password_hash = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Factory roles need a factory
    factory_id = None
    if normalized_role in FACTORY_ROLES:
        # Create or get factory for this company
        factory = db.query(Factory).filter(Factory.name == request.company_name).first()
        if not factory:
            factory = Factory(name=request.company_name, location=request.industry or "Bangladesh")
            db.add(factory)
            db.commit()
            db.refresh(factory)
        factory_id = factory.id
    
    # Create user account immediately
    new_user = User(
        email=request.email,
        hashed_password=password_hash,
        name=request.contact_name,
        role=normalized_role,  # Store normalized backend role
        factory_id=factory_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Create demo request for tracking
    demo_request = DemoRequest(
        company_name=request.company_name,
        industry=request.industry,
        company_size=request.company_size,
        contact_name=request.contact_name,
        email=request.email,
        phone=request.phone,
        password_hash=password_hash,
        role_requested=normalized_role,  # Store normalized role
        message=request.message,
        status="approved",  # Auto-approve since user created
        user_id=new_user.id,
        reviewed_by=new_user.id,
        reviewed_at=datetime.utcnow()
    )
    
    db.add(demo_request)
    db.commit()
    db.refresh(demo_request)
    
    return demo_request

# Admin endpoints
@router.get("/list", response_model=List[DemoRequestResponse])
def list_demo_requests(
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["platform_admin"]))
):
    """
    List all demo requests (admin only)
    Optional filter by status: pending, approved, rejected
    """
    query = db.query(DemoRequest)
    
    if status_filter:
        query = query.filter(DemoRequest.status == status_filter)
    
    requests = query.order_by(DemoRequest.created_at.desc()).all()
    return requests

@router.post("/{request_id}/approve")
def approve_demo_request(
    request_id: int,
    password: str,
    factory_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["platform_admin"]))
):
    """
    Approve demo request and create user account
    Admin only
    """
    demo_request = db.query(DemoRequest).filter(DemoRequest.id == request_id).first()
    
    if not demo_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demo request not found")
    
    if demo_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request already {demo_request.status}"
        )
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == demo_request.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Validate factory_id requirement
    if demo_request.role_requested in ["factory_admin", "manager", "worker"] and not factory_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="factory_id is required for this role"
        )
    
    # Create user account
    hashed_password = get_password_hash(password)
    new_user = User(
        email=demo_request.email,
        hashed_password=hashed_password,
        name=demo_request.contact_name,
        role=demo_request.role_requested,
        factory_id=factory_id
    )
    
    db.add(new_user)
    db.flush()  # Get user ID
    
    # Update demo request
    demo_request.status = "approved"
    demo_request.reviewed_by = current_user.id
    demo_request.reviewed_at = datetime.now()
    demo_request.user_id = new_user.id
    
    db.commit()
    
    return {
        "success": True,
        "message": "Demo request approved and user account created",
        "user_id": new_user.id,
        "email": new_user.email
    }

@router.post("/{request_id}/reject")
def reject_demo_request(
    request_id: int,
    reason: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["platform_admin"]))
):
    """
    Reject demo request
    Admin only
    """
    demo_request = db.query(DemoRequest).filter(DemoRequest.id == request_id).first()
    
    if not demo_request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Demo request not found")
    
    if demo_request.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Request already {demo_request.status}"
        )
    
    # Update demo request
    demo_request.status = "rejected"
    demo_request.reviewed_by = current_user.id
    demo_request.reviewed_at = datetime.now()
    demo_request.admin_notes = reason
    
    db.commit()
    
    return {
        "success": True,
        "message": "Demo request rejected"
    }
