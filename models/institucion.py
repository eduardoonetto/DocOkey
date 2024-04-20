from pydantic import BaseModel #importar la clase base de Pydantic, que nos permite definir modelos de datos.
from typing import Optional #crear campos opcionales.

#Datos de usuario
class Institucion(BaseModel):
    id: Optional[int] = None
    institucion: str
    url_logo: str
    rut_admin: str

#Datos de usuario para el login
class CreateInstitucion(BaseModel):
    institucion: str
    url_logo: str
    rut_admin: str