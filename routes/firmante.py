from fastapi import APIRouter
from database.sqlite import get_firmantes_by_documento_id,get_users_by_institucion


#Rutas de usuarios
router = APIRouter()

#consultar todos los Firmantes de un Documento:
@router.get('/firmante/listar/{documento_id}')
async def get_firmantes(documento_id: int):
    firmantes = get_firmantes_by_documento_id(documento_id)
    return firmantes

#listar Todos los usuarios enrolados en una institucion:
@router.get('/firmante/listar_usuarios/{institucion_id}')
async def get_usuarios(institucion_id: int):
    usuarios = get_users_by_institucion(institucion_id)
    return usuarios