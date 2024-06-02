from pydantic import BaseModel #importar la clase base de Pydantic, que nos permite definir modelos de datos.
from typing import Optional #crear campos opcionales.

class Firmante(BaseModel):
    signer_rut: str
    signer_role: str
    signer_institucion: Optional[str]
    signer_name: str
    signer_email: str
    signer_type: int

class Firma(BaseModel):
  user_password: str
  tipo_accion: int
  id_documento: int
  role: str
