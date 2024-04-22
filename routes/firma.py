from fastapi import APIRouter


#Rutas de usuarios
router = APIRouter()

#funcion para firmar un documento con un firmante, añadir Audit, fecha_firma y deshabilitar el campo 'habilitado' a 0 en firmante:
@router.post('/firmas/firmar/{documento_id}/{firmante_id}')
async def firmar_documento(documento_id: int, firmante_id: int):
    return {"documento_id": documento_id, "firmante_id": firmante_id}
