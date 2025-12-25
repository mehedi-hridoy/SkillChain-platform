from pydantic import BaseModel
from typing import Optional

class ComplianceEventCreate(BaseModel):
    factory_id: int
    user_id: int
    event_type: str
    status: str
    area: str
    evidence_url: Optional[str] = None
    batch_id: Optional[int] = None


class ComplianceEventResponse(BaseModel):
    id: int
    factory_id: int
    user_id: int
    event_type: str
    status: str
    area: str
    evidence_url: Optional[str]
    batch_id: Optional[int]

    class Config:
        from_attributes = True
