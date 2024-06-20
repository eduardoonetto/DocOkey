from fastapi import APIRouter, HTTPException, Depends
from models.documentos import Documentos
from models.document_action import DocumentAction
from database.sqlite import (
    add_documento,
    get_document_by_rut,
    sign_document,
    reject_document,
    create_audit_entry,
    log_action,
    getDocument
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
@router.get('/documento/listar/{signer_rut}')
async def get_documentos(signer_rut: str):
    return get_document_by_rut(signer_rut)

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

# Obtener 1 documento:
@router.get("/documento/{document_id}")
async def get_document(document_id: int):
    return getDocument(document_id)[0]


#Obtener mis documentos firmados:
@router.get("/documento/signed/{rut}")
async def get_signed_documents(rut: str):
    return get_documentSigned_by_rut(rut)

@router.get("/view-pdf/{id_documento}")
async def view_pdf(id_documento: int):
    try:
        # Decode the base64 PDF
        base64_pdf = getDocument(id_documento)[0][4]
        pdf_data = base64.b64decode(base64_pdf)
        pdf_io = io.BytesIO(pdf_data)
        # Create a StreamingResponse to serve the PDF
        response = StreamingResponse(pdf_io, media_type="application/pdf")
        response.headers["Content-Disposition"] = "inline; filename=example.pdf"
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))