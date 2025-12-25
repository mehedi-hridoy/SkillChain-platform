from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import func
from app.db.base import Base

class Product(Base):
    """
    Digital Product Passport (DPP) - EU Compliant
    Each product has unique QR code linking to public transparency page
    """
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    factory_id = Column(Integer, ForeignKey("factories.id"), nullable=False)

    # Basic Product Info
    sku = Column(String, nullable=False, unique=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Product Category
    category = Column(String, nullable=True)  # e.g. "T-Shirt", "Jeans", "Jacket"
    
    # DPP Unique Identifier (used in QR code)
    dpp_id = Column(String, unique=True, index=True, nullable=False)  # UUID format
    
    # Material Composition (EU requirement)
    materials = Column(JSON, nullable=True)  
    # e.g. [{"material": "Cotton", "percentage": 95}, {"material": "Elastane", "percentage": 5}]
    
    # Origin & Supply Chain
    origin_country = Column(String, nullable=True)
    raw_material_source = Column(String, nullable=True)
    
    # Environmental Data (EU requirement)
    carbon_footprint_kg = Column(Float, nullable=True)  # CO2 equivalent
    water_usage_liters = Column(Float, nullable=True)
    recycled_content_percentage = Column(Float, nullable=True)
    
    # Certifications (links to compliance documents)
    certifications = Column(JSON, nullable=True)
    # e.g. ["OEKO-TEX", "GOTS", "Fair Trade"]
    
    # Images
    product_images = Column(JSON, nullable=True)  # Array of image URLs
    
    # QR Code
    qr_code_url = Column(String, nullable=True)  # Generated QR code image
    
    # Batch tracking
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)
    
    # Compliance Status
    compliance_verified = Column(Boolean, default=False)
    compliance_score = Column(Integer, nullable=True)  # 0-100
    
    # Timestamps
    manufactured_date = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
