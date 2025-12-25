from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # worker, manager, factory_admin, buyer, platform_admin
    factory_id = Column(Integer, ForeignKey("factories.id"), nullable=True)  # nullable for platform_admin, buyer
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships for content
    articles = relationship("Article", back_populates="author")
    courses = relationship("Course", back_populates="instructor")

