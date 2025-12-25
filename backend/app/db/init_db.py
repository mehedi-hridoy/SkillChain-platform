from app.db.base import Base
from app.db.session import engine
# Import all models to ensure they are registered with SQLAlchemy
from app.models.factory import Factory
from app.models.user import User
from app.models.complience_event import ComplianceEvent

def init_db():
    Base.metadata.create_all(bind=engine)
