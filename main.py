from fastapi            import FastAPI, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
#Rutas
from routes.users       import router as user_router
from routes.institucion import router as institucion_router
from routes.roles       import router as roles_router
from routes.documentos  import router as documentos_router
from routes.firmante    import router as firmante_router
#Queries
from database.sqlite    import initialize_database
from utils.session_validation import session_id_valid
import time

#Inicia el cliente API
app = FastAPI()


@app.middleware("http")
async def session_middleware(request: Request, call_next):
    # Obtenemos el path de la solicitud
    path = request.url.path

    # Excluir validación para el endpoint de login
    if path == "/login" or path == "/docs" or path == "/openapi.json" or path == "/users/registro":
        response = await call_next(request)
        return response

    session_id = request.headers.get("Authorization")

    if not session_id_valid(session_id):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Session_id Invalida o session expirada."}
        )

    response = await call_next(request)
    return response

#Crea o añade nuevas tablas a la base de datos
initialize_database()

#Añade las rutas
app.include_router(user_router)
app.include_router(institucion_router)
app.include_router(roles_router)
app.include_router(documentos_router)
app.include_router(firmante_router)