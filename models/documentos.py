from pydantic import BaseModel #importar la clase base de Pydantic, que nos permite definir modelos de datos.
from typing import Optional #crear campos opcionales.
import datetime
from models.firmante import Firmante



#Datos de usuario
class Documentos(BaseModel):
    nombre_documento: str
    archivo_b64: str
    institucion_id: int
    fecha_creacion: Optional[str] = datetime.datetime.now().strftime("%d-%m-%Y")
    signers: list[Firmante]

