from fastapi import APIRouter, HTTPException, Depends
from models.documentos import Documentos
from models.document_action import DocumentAction
from database.sqlite import (
    add_documento,
    get_documentos_by_rut_and_institucion_id,
    sign_document,
    reject_document,
    create_audit_entry,
    log_action
)
import hashlib
from datetime import datetime
from fastapi.security import APIKeyHeader

router = APIRouter()
session_id = APIKeyHeader(name="Authorization")

# Subir Documento a tabla documentos
@router.post('/documento/subir')
async def upload_file(documento: Documentos, Authorization: str = Depends(session_id)):
    response = add_documento(documento.nombre_documento, documento.archivo_b64, documento.institucion_id, documento.fecha_creacion, documento.signers, Authorization)
    return response

# Listar Documentos de un firmante según su signer_rut e institucion_id
@router.get('/documento/listar/{signer_rut}/{signer_institucion}')
async def get_documentos(signer_rut: str, signer_institucion: str):
    return get_documentos_by_rut_and_institucion_id(signer_rut, signer_institucion)

# Manejar acción de documento (firmar o rechazar)
@router.post("/document/action")
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
