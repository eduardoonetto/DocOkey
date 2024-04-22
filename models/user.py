from pydantic import BaseModel #importar la clase base de Pydantic, que nos permite definir modelos de datos.
from typing import Optional #crear campos opcionales.

#Datos de usuario
class User(BaseModel):
    id: Optional[int] = None
    username: str
    rut: str
    email: str
    password: str

#Datos de usuario para el login
class LoginUser(BaseModel):
    user_rut: str
    user_password: str