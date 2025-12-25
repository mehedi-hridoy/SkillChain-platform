from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
import uuid
import os

from app.core.dependencies import get_db, get_current_user, require_role
from app.models.batch import Batch
from app.models.product import Product
from app.models.factory import Factory
from app.models.complience_event import ComplianceEvent
from app.models.user import User
from app.services.qrcode_service import QRCodeService
from app.services.file_upload import FileUploadService

router = APIRouter(prefix="/dpp", tags=["Digital Product Passport"])

# Schemas
class MaterialComposition(BaseModel):
    material: str
    percentage: float
    origin: Optional[str] = None
    certification: Optional[str] = None

class ProductCreate(BaseModel):
    sku: str
    name: str
    description: Optional[str] = None
    category: str
    materials: List[MaterialComposition]
    origin_country: str
    raw_material_source: Optional[str] = None
    carbon_footprint_kg: Optional[float] = None
    water_usage_liters: Optional[float] = None
    recycled_content_percentage: Optional[float] = None
    certifications: Optional[List[str]] = None
    manufactured_date: Optional[str] = None

class ProductResponse(BaseModel):
    id: int
    sku: str
    name: str
    dpp_id: str
    qr_code_url: Optional[str]
    factory_id: int
    
    class Config:
        from_attributes = True

class DPPPublicResponse(BaseModel):
    dpp_id: str
    product_name: str
    category: str
    sku: str
    manufacturer: dict
    materials: List[dict]
    environmental_impact: dict
    certifications: List[str]
    compliance_status: dict
    supply_chain: dict
    manufactured_date: Optional[str]
    qr_code_url: str


@router.post("/products", response_model=ProductResponse)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["factory_admin", "manager", "platform_admin"]))
):
    """
    Create a new product with Digital Product Passport
    Generates unique DPP ID and QR code
    """
    try:
        # Check if SKU already exists
        existing = db.query(Product).filter(Product.sku == product.sku).first()
        if existing:
            raise HTTPException(status_code=400, detail="SKU already exists")
        
        # Generate unique DPP ID
        dpp_id = str(uuid.uuid4())
        
        # Get factory info
        factory = db.query(Factory).filter(Factory.id == current_user.factory_id).first()
        if not factory:
            raise HTTPException(status_code=404, detail="Factory not found")
        
        # Convert materials to JSON format
        materials_json = [m.dict() for m in product.materials]
        
        # Create product
        new_product = Product(
            factory_id=current_user.factory_id,
            sku=product.sku,
            name=product.name,
            description=product.description,
            category=product.category,
            dpp_id=dpp_id,
            materials=materials_json,
            origin_country=product.origin_country,
            raw_material_source=product.raw_material_source,
            carbon_footprint_kg=product.carbon_footprint_kg,
            water_usage_liters=product.water_usage_liters,
            recycled_content_percentage=product.recycled_content_percentage,
            certifications=product.certifications or [],
            manufactured_date=datetime.fromisoformat(product.manufactured_date) if product.manufactured_date else None,
            compliance_verified=False
        )
        
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        
        # Generate QR code
        dpp_url = f"{os.getenv('FRONTEND_URL', 'http://localhost:3001')}/dpp/{dpp_id}"
        qr_service = QRCodeService()
        qr_filepath = qr_service.save_qr_code(
            data=dpp_url,
            filename=f"dpp_{dpp_id}.png",
            directory="uploads/qrcodes"
        )
        
        # Extract just the filename from the full path
        qr_filename = os.path.basename(qr_filepath)
        
        # Update product with QR code URL
        new_product.qr_code_url = f"/files/qrcodes/{qr_filename}"
        db.commit()
        
        return new_product
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/products")
def list_products(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all products for the user's factory
    """
    query = db.query(Product)
    
    # Filter by factory for non-admin users
    if current_user.role != "platform_admin":
        query = query.filter(Product.factory_id == current_user.factory_id)
    
    products = query.offset(skip).limit(limit).all()
    return products


@router.get("/products/{product_id}")
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed product information
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
        # Check access
        if current_user.role != "platform_admin" and product.factory_id != current_user.factory_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        factory = db.query(Factory).filter(Factory.id == product.factory_id).first()
        
        # Get compliance events for this product
        events = db.query(ComplianceEvent).filter(
            ComplianceEvent.factory_id == product.factory_id
        ).order_by(ComplianceEvent.created_at.desc()).limit(10).all()
        
        return {
            "product": product,
            "factory": factory,
            "recent_compliance_events": [
                {
                    "event_type": e.event_type,
                    "status": e.status,
                    "area": e.area,
                    "created_at": e.created_at
                }
                for e in events
            ]
        }


@router.post("/products/{product_id}/images")
async def upload_product_image(
    product_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["factory_admin", "manager"]))
):
    """
    Upload product images for DPP
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
        
        if product.factory_id != current_user.factory_id:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Upload image
        file_service = FileUploadService()
        result = await file_service.save_file(file, "products")
        
        # Add to product images
        images = product.product_images or []
        images.append(result["url"])
        product.product_images = images
        
        db.commit()
        
        return {"message": "Image uploaded", "url": result["url"]}


# PUBLIC ENDPOINTS (No authentication required)
public_router = APIRouter(prefix="/public/dpp", tags=["Public DPP"])

@public_router.get("/{dpp_id}")
def get_public_dpp(dpp_id: str, db: Session = Depends(get_db)):
    """
    Public endpoint - Anyone can view DPP by scanning QR code
    Returns complete product passport information
    """
    # Find product by DPP ID
    product = db.query(Product).filter(Product.dpp_id == dpp_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Digital Product Passport not found")
        
        # Get factory info
        factory = db.query(Factory).filter(Factory.id == product.factory_id).first()
        
        # Get compliance events
        compliance_events = db.query(ComplianceEvent).filter(
            ComplianceEvent.factory_id == product.factory_id
        ).order_by(ComplianceEvent.created_at.desc()).all()
        
        # Calculate compliance score
        total_events = len(compliance_events)
        passed_events = sum(1 for e in compliance_events if e.status == "PASS")
        compliance_rate = round((passed_events / total_events * 100), 1) if total_events > 0 else 0
        
        # Get latest compliance checks by type
        compliance_by_type = {}
        for event in compliance_events:
            if event.event_type not in compliance_by_type:
                compliance_by_type[event.event_type] = {
                    "status": event.status,
                    "date": event.created_at.isoformat() if event.created_at else None,
                    "area": event.area
                }
        
        return {
            "dpp_id": product.dpp_id,
            "product_name": product.name,
            "category": product.category,
            "sku": product.sku,
            "description": product.description,
            "manufacturer": {
                "name": factory.name,
                "location": factory.location,
                "id": factory.id
            },
            "materials": product.materials or [],
            "environmental_impact": {
                "carbon_footprint_kg": product.carbon_footprint_kg,
                "water_usage_liters": product.water_usage_liters,
                "recycled_content_percentage": product.recycled_content_percentage
            },
            "certifications": product.certifications or [],
            "origin": {
                "country": product.origin_country,
                "raw_material_source": product.raw_material_source
            },
            "compliance_status": {
                "verified": product.compliance_verified,
                "score": compliance_rate,
                "total_checks": total_events,
                "passed_checks": passed_events,
                "by_type": compliance_by_type
            },
            "supply_chain": {
                "manufactured_date": product.manufactured_date.isoformat() if product.manufactured_date else None,
                "batch_tracking": product.batch_id is not None
            },
            "images": product.product_images or [],
            "qr_code_url": product.qr_code_url,
            "last_updated": product.updated_at.isoformat() if product.updated_at else product.created_at.isoformat()
        }


@public_router.get("/verify/{dpp_id}")
def verify_dpp(dpp_id: str, db: Session = Depends(get_db)):
    """
    Quick verification endpoint - Check if DPP is valid
    """
    product = db.query(Product).filter(Product.dpp_id == dpp_id).first()
    
    if not product:
        return {"valid": False, "message": "Invalid DPP ID"}
    
    return {
        "valid": True,
        "product_name": product.name,
        "manufacturer": db.query(Factory).filter(Factory.id == product.factory_id).first().name,
        "compliance_verified": product.compliance_verified
    }


router.include_router(public_router)
