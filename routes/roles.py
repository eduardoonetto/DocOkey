from fastapi import APIRouter
from models.roles import Roles
from database.sqlite import add_roles, get_role_by_institution

#Rutas de usuarios
router = APIRouter()

#INSERTAR:
@router.post('/addRole')
async def add_roles_routes(roles: Roles):
    print(roles.institucion_id, roles.user_id, roles.role)
    add_roles(roles.institucion_id, roles.user_id, roles.role)
    return roles

#CONSULTAR roles by institucion:
@router.get('/roles_by_institution/{institucion_id}')
async def get_role_routes(institucion_id: int):
    print(institucion_id)
    print(get_role_by_institution(institucion_id))