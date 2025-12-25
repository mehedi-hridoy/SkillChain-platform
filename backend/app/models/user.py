from sqlalchemy import Column, Integer, String, ForeignKey
from app.db.base import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # worker, supervisor, manager
    factory_id = Column(Integer, ForeignKey("factories.id"), nullable=False)
