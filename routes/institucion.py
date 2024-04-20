from fastapi import APIRouter
from models.institucion import Institucion
from database.sqlite import create_institucion, get_instituciones, get_institucion

#Rutas de usuarios
router = APIRouter()

#INSERTAR:
@router.post('/institucion/registro')
async def create_institucion_routes(institucion: Institucion):
    create_institucion(institucion.institucion, institucion.url_logo, institucion.rut_admin)
    return institucion

#CONSULTAR ALL:
@router.get('/instituciones')
async def get_instituciones_routes():
    return get_instituciones()

#CONSULTAR ONE:
@router.get('/instituciones/{id}')
async def get_institucion_routes(id: int):
    users = get_institucion(id)
    if users:
        return users
    return 'User not found'


