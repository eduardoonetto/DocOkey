from fastapi import APIRouter, Depends
from database.sqlite import get_firmantes_by_documento_id, get_users_by_institucion, get_user_rut_by_session_id, validate_user, create_audit_entry
from fastapi.security import APIKeyHeader
from models.firmante import Firma
from datetime import datetime
import hashlib

#Rutas de usuarios
router = APIRouter()
session_id = APIKeyHeader(name="Authorization")

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

#Firmar Documentos:
@router.post('/firmante/firmar')
async def firmar_documento(firma: Firma, Authorization: str = Depends(session_id)):

    #Obtener Session_id y usar funcion para traer el rut del firmante:
    rut_user = get_user_rut_by_session_id(Authorization)
    #validar que el user_rut y user_password coincidan con la base de datos:
    if not validate_user(rut_user, firma.user_password):
        return {'msg': 'Password Incorrecta', 'status': 'ERROR'}
    #crear hash de auditoria:
    audit_info = f"{Authorization[:6]}-{rut_user}-{firma.role}-{firma.id_documento}-{datetime.now()}"
    audit_hash = hashlib.sha256(audit_info.encode()).hexdigest()
    #Firmar o Rechazar el documento:
    isSign = create_audit_entry(audit_hash, firma.id_documento, rut_user, firma.role, firma.tipo_accion)
    if isSign:
        return {'audit': audit_hash, 'msg': 'Documento Firmado', 'status': 'OK', 'document_id': firma.id_documento}
    else:
        return {'msg': 'Documento ya fue firmado o no corresponde el firmante', 'status': 'ERROR'}