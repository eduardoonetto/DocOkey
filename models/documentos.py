from sqlalchemy import Column, Integer, String, Boolean, DateTime
from database import Base
import datetime
from models.firmante import Firmante

# Datos de usuario
class Documentos(BaseModel):
    nombre_documento: str
    archivo_b64: str
    institucion_id: int
    fecha_creacion: Optional[str] = datetime.datetime.now().strftime("%d-%m-%Y")
    signers: List[Firmante]
