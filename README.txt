def get_roles():
    #traer todos los roles y mostrar el rut del usuario y el nombre de la institucion:
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT uir.id, u.username, i.institucion, uir.role
        FROM users_institucion_roles uir
        JOIN users u ON uir.user_id = u.id
        JOIN institucion i ON uir.institucion_id = i.id
    ''')
    roles = cursor.fetchall()
    roles = [
        {
            'id': role[0],
            'username': role[1],
            'institucion': role[2],
            'role': role[3]
        }
        for role in roles
    ]
    connection.close()
    return roles


Documentos
----------
Id
archivo_b64
nombre_documento
Institucion_id

Firmantes
--------
id
Rut_firmante
documento_id
tipo_firma

empujar aplicacion:
uvicorn main:app --reload
