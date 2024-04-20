from pydantic import BaseModel #importar la clase base de Pydantic, que nos permite definir modelos de datos.
from typing import Optional #crear campos opcionales.

#Datos de usuario
class Document(BaseModel):
    nombre_documento: str
    archivo_b64: int
    institucion_id: int
    fecha_creacion: str
    