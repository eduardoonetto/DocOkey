from fastapi import FastAPI
from routes.users import router as user_router
from routes.institucion import router as institucion_router
from routes.roles import router as roles_router
from database.sqlite import initialize_database

#Inicia el cliente API
app = FastAPI()
#Crea o añade nuevas tablas a la base de datos
initialize_database()
#Añade las rutas
app.include_router(user_router)
app.include_router(institucion_router)
app.include_router(roles_router)