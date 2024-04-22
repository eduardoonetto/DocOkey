from fastapi import APIRouter
from models.user import User, LoginUser
from database.sqlite import create_user, get_users, get_user, login_user

#Rutas de usuarios
router = APIRouter()

#INSERTAR:
@router.post('/users/registro')
async def create_user_routes(user: User):
    create_user(user.username,user.rut, user.email, user.password)
    return user

#CONSULTAR ALL:
@router.get('/users')
async def get_users_routes():
    return get_users()

#CONSULTAR ONE:
@router.get('/users/{id}')
async def get_user_routes(id: int):
    users = get_user(id)
    if users:
        return users
    return 'User not found'

#login
@router.post('/login')
async def login_user_routes(user: LoginUser):
    return login_user(user.user_rut, user.user_password)
    


