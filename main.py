from fastapi import FastAPI, Depends, HTTPException, Request, status
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
import time
from fastapi.middleware.cors import CORSMiddleware
from models.document_action import DocumentAction
from database.sqlite import sign_document, reject_document, create_audit_entry, log_action
import hashlib
from datetime import datetime

# Inicia el cliente API
app = FastAPI()

# Configuración de CORS para permitir solicitudes desde el origen de tu aplicación Ionic
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost:8100", "http://localhost:8100", "http://localhost:8100/", "http://localhost:8100", "http://localhost:8100/"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.middleware("http")
async def session_middleware(request: Request, call_next):
    # Obtenemos el path de la solicitud
    path = request.url.path

    # Excluir validación para el endpoint de login
    if path in ["/login", "/docs", "/openapi.json", "/users/registro"]:
        response = await call_next(request)
        return response

    session_id = request.headers.get("Authorization")

    if not session_id_valid(session_id):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"message": "Session Invalida o session expirada."}
        )

    response = await call_next(request)
    return response

@app.post("/document/action")
async def handle_document_action(action: DocumentAction):
    if action.action == "sign":
        sign_document(action.document_id)
    elif action.action == "reject":
        reject_document(action.document_id)
    else:
        raise HTTPException(status_code=400, detail="Acción no válida. Use 'sign' o 'reject'.")

    # Generar la cadena combinada y hashearla
    audit_info = f"{action.session_id[:6]}-{action.rut}-{action.role}-{action.document_id}-{datetime.now()}"
    audit_hash = hashlib.sha256(audit_info.encode()).hexdigest()
    
    # Guardar la información hasheada en el campo de auditoría
    create_audit_entry(action.document_id, audit_hash)

    # Registrar la acción en el registro de cambios
    log_action(action.session_id, action.action, action.document_id)

    return {"message": f"Documento {action.document_id} {action.action}ado."}  # Se retorna un mensaje de éxito

# Crea o añade nuevas tablas a la base de datos
initialize_database()

# Añade las rutas
app.include_router(user_router)
app.include_router(institucion_router)
app.include_router(roles_router)
app.include_router(documentos_router)
app.include_router(firmante_router)
app.include_router(firma_router)
