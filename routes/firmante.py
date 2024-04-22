from fastapi import APIRouter
from database.sqlite import get_firmantes_by_documento_id


#Rutas de usuarios
router = APIRouter()

#consultar todos los Firmantes de un Documento:
@router.get('/firmante/listar/{documento_id}')
async def get_firmantes(documento_id: int):
    firmantes = get_firmantes_by_documento_id(documento_id)
    return firmantes
