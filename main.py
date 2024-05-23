from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
# Rutas
from routes.users import router as user_router
from routes.institucion import router as institucion_router
from routes.roles import router as roles_router
from routes.documentos import router as documentos_router
from routes.firmante import router as firmante_router
from routes.firma import router as firma_router
# Queries
from database.sqlite import initialize_database
from utils.session_validation import session_id_valid
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

# Inicia el cliente API
app = FastAPI()

# Configuración de CORS para permitir solicitudes desde el origen de tu aplicación Ionic
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8100"],  # Corrige la URL, elimina la barra diagonal al final
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para agregar encabezados CORS a todas las respuestas
class AddCORSHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:8100'
        response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS, PUT, DELETE'
        response.headers['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
        return response

app.add_middleware(AddCORSHeadersMiddleware)

@app.middleware("http")
async def print_request_headers(request: Request, call_next):
    headers = request.headers
    # Imprimir los encabezados en la consola
    print("Request headers:")
    print(headers)
    session_id = request.headers.get("Authorization")
    print(f"Session ID: {session_id}")

    path = request.url.path
    if path in ["/login", "/docs", "/openapi.json", "/users/registro"] or request.method == "OPTIONS":
        response = await call_next(request)
        return response

    print("Validating session ID")
    if not session_id or not session_id_valid(session_id):
        return JSONResponse(status_code=401, content={"message": "Unauthorized"})

    # Continuar con la solicitud
    response = await call_next(request)
    return response

@app.options("/{rest_of_path:path}")
async def preflight_handler(rest_of_path: str):
    return JSONResponse(status_code=200, headers={
        'Access-Control-Allow-Origin': 'http://localhost:8100',
        'Access-Control-Allow-Methods': 'POST, GET, OPTIONS, PUT, DELETE',
        'Access-Control-Allow-Headers': 'Authorization, Content-Type'
    })

# Crea o añade nuevas tablas a la base de datos
initialize_database()

# Añade las rutas
app.include_router(user_router)
app.include_router(institucion_router)
app.include_router(roles_router)
app.include_router(documentos_router)
app.include_router(firmante_router)
app.include_router(firma_router)
