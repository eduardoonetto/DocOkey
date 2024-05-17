from pydantic import BaseModel

class DocumentAction(BaseModel):
    document_id: int
    action: str  # 'sign' o 'reject'
    session_id: str
    rut: str
    role: str
