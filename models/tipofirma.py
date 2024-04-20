from pydantic import BaseModel #importar la clase base de Pydantic, que nos permite definir modelos de datos.
from typing import Optional #crear campos opcionales.

#Datos de usuario
class Document(BaseModel):
    id: Optional[int] = None
    tipo_firma: str
