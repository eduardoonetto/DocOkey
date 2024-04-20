from fastapi import APIRouter
from models.documentos import Documentos
from database.sqlite import add_documento, get_documentos_by_rut_and_institucion_id

#Rutas de usuarios
router = APIRouter()

#Subir Documento a tabla documentos:
@router.post('/documento/subir')
async def upload_file(documento: Documentos):
    print(documento.nombre_documento, documento.archivo_b64, documento.institucion_id, documento.fecha_creacion)
    documento_id = add_documento(documento.nombre_documento, documento.archivo_b64, documento.institucion_id, documento.fecha_creacion, documento.signers)
    return {documento.nombre_documento: documento.nombre_documento, "documento_id": documento_id}

#listar Documentos de un firmante segun su signer_rut e institucion_id:
@router.get('/documento/listar/{signer_rut}/{signer_institucion}')
async def get_documentos(signer_rut: str, signer_institucion: str):
    return get_documentos_by_rut_and_institucion_id(signer_rut, signer_institucion)