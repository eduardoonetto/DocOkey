from pydantic import BaseModel
from typing import Optional, List
import datetime
from models.firmante import Firmante

# Datos de usuario
class Documentos(BaseModel):
    nombre_documento: str
    archivo_b64: str
    institucion_id: int
    fecha_creacion: Optional[str] = datetime.datetime.now().strftime("%d-%m-%Y")
    signers: List[Firmante]
    signed: bool = False  # Nuevo campo para indicar si el documento está firmado
