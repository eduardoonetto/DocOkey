from pydantic import BaseModel #importar la clase base de Pydantic, que nos permite definir modelos de datos.
from typing import Optional #crear campos opcionales.

#Datos de usuario
class Firmante(BaseModel):
    rut_firmante: str
    tipo_firma: str
    documento_id: int
