from pydantic import BaseModel #importar la clase base de Pydantic, que nos permite definir modelos de datos.
from typing import Optional #crear campos opcionales.

#Datos de usuario
class Roles(BaseModel):
    user_id: int
    institucion_id: int
    role: str
