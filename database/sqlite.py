import sqlite3
import hashlib
import time
from datetime import datetime

def initialize_database():
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rut TEXT NOT NULL,
            username TEXT NOT NULL,
            email TEXT NOT NULL,
            password TEXT NOT NULL
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS institucion(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            institucion TEXT NOT NULL,
            url_logo TEXT NOT NULL,
            rut_admin TEXT NOT NULL
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            expiration_timestamp INTEGER,
            user_rut TEXT NOT NULL
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_institucion_roles(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INT NOT NULL,
            institucion_id INT NOT NULL,
            role TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(institucion_id) REFERENCES institucion(id)
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documentos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            fecha_creacion TEXT NOT NULL,
            archivo_b64 TEXT NOT NULL,
            institucion_id INT NOT NULL,
            FOREIGN KEY(institucion_id) REFERENCES institucion(id)
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tipo_firma(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo_firma TEXT NOT NULL
        );
    ''')
    
    cursor.execute('''
        SELECT * FROM tipo_firma WHERE tipo_firma = 'Firmar con Pin'
    ''')
    tipo_firma = cursor.fetchone()
    if not tipo_firma:
        cursor.execute('''
            INSERT INTO tipo_firma(tipo_firma)
            VALUES('Firmar con Pin')
        ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS firmantes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            signer_rut TEXT NOT NULL,
            signer_role TEXT NOT NULL,
            signer_institucion TEXT NOT NULL,
            signer_name TEXT NOT NULL,
            signer_email TEXT NOT NULL,
            signer_type TEXT NOT NULL,
            documento_id INT NOT NULL,
            audit TEXT,
            fecha_firma TEXT,
            habilitado int default 1,
            tipo_accion int default 0,
            FOREIGN KEY(documento_id) REFERENCES documentos(id)
        );
    ''')
    #tipo_accion: 0 para pendiente, 1 para firmado, 2 para rechazado
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registro_cambios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            accion TEXT NOT NULL,
            document_id INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(document_id) REFERENCES documentos(id)
        );
    ''')
    
    connection.commit()
    connection.close()

def create_user(username: str, rut: str, email: str, password: str):
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    #validar que el rut no exista previamente
    cursor.execute('''
        SELECT * FROM users WHERE rut = ?
    ''', (rut,))
    user = cursor.fetchone()
    if user:
        connection.close()
        return {'msg': 'El rut ya existe', 'status': 'ERROR'}
    else:
        #se crea el usuario:
        cursor.execute('''
            INSERT INTO users(username, rut, email, password)
            VALUES(?, ?, ?, ?)
        ''', (username, rut, email, password))
        #cuando se cree un usuario, debe crearse una institucion personal para el usuario se dejara logo por defecto.
        cursor.execute('''
            INSERT INTO institucion(institucion, url_logo, rut_admin)
            VALUES(?, ?, ?)
        ''', (username.replace(" ", "_"), 'Personal', rut))
        #añadir rol personal al usuario en su institucion personal
        cursor.execute('''
            SELECT id FROM users WHERE rut = ?
        ''', (rut,))
        user = cursor.fetchone()
        if user:
            cursor.execute('''
                SELECT id FROM institucion WHERE rut_admin = ? and institucion = ?
            ''', (rut, username.replace(" ", "_")))
            institucion = cursor.fetchone()
            if institucion:
                cursor.execute('''
                    INSERT INTO users_institucion_roles(user_id, institucion_id, role)
                    VALUES(?, ?, ?)
                ''', (user[0], institucion[0], 'personal'))
                connection.commit()
                connection.close()
                return {'msg': 'Usuario creado', 'status': 'OK', 'user_id': user[0], 'username': username, 'rut': rut, 'email': email}

def get_users():
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users')
    # fetchall() devuelve una lista (array) con todos los registros
    users = cursor.fetchall()
    # añadir key al value retornado
    users = [
        {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'password': user[3]
        }
        for user in users
    ]
    connection.close()
    return users

# Traer 1 usuario:
def get_user(id: int):
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (id,))
    user = cursor.fetchone()
    # agregar key al value retornado
    if user:
        user = {
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'password': user[3]
        }
    connection.close()
    return user

# INSTITUCIONES

def create_institucion(institucion: str, url_logo: str, rut_admin: str):
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO institucion(institucion, url_logo, rut_admin)
        VALUES(?, ?, ?)
    ''', (institucion, url_logo, rut_admin))
    connection.commit()
    # Crear un usuario con el rol de administrador segun rut_admin en tabla users_institucion_roles
    cursor.execute('''
        SELECT id FROM users WHERE rut = ?
    ''', (rut_admin,))
    user = cursor.fetchone()
    if user:
        cursor.execute('''
            INSERT INTO users_institucion_roles(user_id, institucion_id, role)
            VALUES(?, ?, ?)
        ''', (user[0], cursor.lastrowid, 'admin'))
        connection.commit()
    connection.close()

def get_instituciones():
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM institucion')
    # fetchall() devuelve una lista (array) con todos los registros
    instituciones = cursor.fetchall()
    # añadir key al value retornado
    instituciones = [
        {
            'id': institucion[0],
            'institucion': institucion[1],
            'url_logo': institucion[2],
            'rut_admin': institucion[3]
        }
        for institucion in instituciones
    ]
    connection.close()
    return instituciones

# Traer 1 institucion:
def get_institucion(id: int):
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM institucion WHERE id = ?', (id,))
    institucion = cursor.fetchone()
    # agregar key al value retornado
    if institucion:
        institucion = {
            'id': institucion[0],
            'institucion': institucion[1],
            'url_logo': institucion[2],
            'rut_admin': institucion[3]
        }
    connection.close()
    return institucion

# ROLES

def add_roles(institucion_id: int, user_id: int, role: str):
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO users_institucion_roles(user_id, institucion_id, role)
        VALUES(?, ?, ?)
    ''', (user_id, institucion_id, role))
    connection.commit()
    connection.close()



def get_role_by_institution(institucion: int):
    # Consultar un institucion por id y mostrar todos los usuarios de esa institucion con sus roles.
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT uir.id, u.username, u.rut, i.institucion, uir.role
        FROM users_institucion_roles uir
        JOIN users u ON uir.user_id = u.id
        JOIN institucion i ON uir.institucion_id = i.id
        WHERE i.id = ?
    ''', (institucion,))
    roles = cursor.fetchall()
    roles = [
        {
            'id': role[0],
            'username': role[1],
            'rut': role[2],
            'institucion': role[3],
            'role': role[4]
        }
        for role in roles
    ]
    return roles

def get_role_by_rut(rut: str, role: str = None):
    # Consultar un usuario por rut y mostrar todas las instituciones a las que pertenece con sus roles.
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    if role:
        cursor.execute('''
            SELECT i.institucion
            FROM users_institucion_roles uir
            JOIN users u ON uir.user_id = u.id
            JOIN institucion i ON uir.institucion_id = i.id
            WHERE u.rut = ? AND uir.role = ?
        ''', (rut, role))
        instituciones_vinculadas = cursor.fetchall()
        #devolver solo el nombre de la institucion {institucion: [nombre_institucion, nombre_institucion]}:
        instituciones_vinculadas = {
            'instituciones': [institucion[0] for institucion in instituciones_vinculadas]
        }
        return instituciones_vinculadas
    else:
        cursor.execute('''
            SELECT uir.id, u.username, u.rut, i.institucion, uir.role
            FROM users_institucion_roles uir
            JOIN users u ON uir.user_id = u.id
            JOIN institucion i ON uir.institucion_id = i.id
            WHERE u.rut = ?
        ''', (rut,))
    roles = cursor.fetchall()
    roles = [
        {
            'id': role[0],
            'username': role[1],
            'rut': role[2],
            'institucion': role[3],
            'role': role[4]
        }
        for role in roles
    ]
    return roles

# DOCUMENTOS

def add_documento(nombre: str, archivo_b64: str, institucion_id: int, fecha_creacion: str, signers: list, session_id: str):
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    #Si la institucion no existe o es Personal, no se puede agregar un documento:
    cursor.execute('''
        SELECT * FROM institucion WHERE id = ?
    ''', (institucion_id,))
    institucion = cursor.fetchone()
    if not institucion or institucion[2] == 'Personal':
        connection.close()
        return {'msg': 'No se puede agregar un documento a esta institucion', 'status': 'ERROR'}
    #Validar que la persona de la session_id tenga un rol admin dentro de la institucion, primero extraer el useR_rut de la session_id:
    user_rut = get_user_rut_by_session_id(session_id)
    cursor.execute('''
        SELECT uir.role FROM users_institucion_roles uir
        JOIN users u ON uir.user_id = u.id
        WHERE u.rut = ? AND uir.institucion_id = ? AND uir.role = 'admin'
    ''', (user_rut, institucion_id))
    user = cursor.fetchone()
    if not user:
        connection.close()
        return {'msg': 'No tienes permisos para agregar un documento a esta institucion', 'status': 'ERROR'}
    #Validar que los firmantes tengan el rol dentro de la institucion:
    for signer in signers:
        #primero extraer el user_id del firmante:
        cursor.execute('''
            SELECT id FROM users WHERE rut = ?
        ''', (signer.signer_rut,))
        
        user = cursor.fetchone()
        if not user:
            connection.close()
            return {'msg': 'El firmante no existe', 'status': 'ERROR'}
    
        #Extraer institucion_id desde el signer_institucion:
        #si signer_institucion es Personal Omitir esta validacion y obtener el user_id del firmante:
        if signer.signer_institucion != 'Personal':
            cursor.execute('''
                SELECT id FROM institucion WHERE institucion = ?
            ''', (signer.signer_institucion,))
            institucion = cursor.fetchone()
            if not institucion:
                connection.close()
                return {'msg': 'La institucion del firmante no existe', 'status': 'ERROR'}
            #Validar que signer_role y signer_institucion coincidan con la base de datos:
            cursor.execute('''
                SELECT * FROM users_institucion_roles WHERE user_id = ? AND role = ? AND institucion_id = ?
            ''', (user[0], signer.signer_role, institucion[0]))
            user = cursor.fetchone()
            if not user:
                connection.close()
                return {'msg': 'El firmante no tiene el rol correcto en la institucion', 'status': 'ERROR'}
    #Si la persona de la session_id tiene un rol admin dentro de la institucion, se puede agregar un documento:
    cursor.execute('''
        INSERT INTO documentos(nombre, archivo_b64, institucion_id, fecha_creacion)
        VALUES (?, ?, ?, ?)
    ''', (nombre, archivo_b64, institucion_id, fecha_creacion))
    documento_id = cursor.lastrowid
    for signer in signers:
        cursor.execute('''
            INSERT INTO firmantes(signer_rut, signer_role, signer_institucion, signer_name, signer_email, signer_type, documento_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (signer.signer_rut, signer.signer_role, signer.signer_institucion, signer.signer_name, signer.signer_email, signer.signer_type, documento_id))
    connection.commit()
    connection.close()
    return {'msg': 'Documento agregado', 'coddocumento': documento_id ,'status': 'OK'}

def get_documentos_by_rut_and_institucion_id(signer_rut: str, signer_institucion: str):
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT d.nombre, d.fecha_creacion, d.archivo_b64, f.signer_rut, f.signer_role, f.signer_institucion, f.signer_name, f.signer_email, f.signer_type
        FROM documentos d
        JOIN firmantes f ON d.id = f.documento_id
        WHERE f.signer_rut = ? AND f.signer_institucion = ?
    ''', (signer_rut, signer_institucion))
    documentos = cursor.fetchall()
    documentos = [
        {
            'nombre': documento[0],
            'fecha_creacion': documento[1],
            'archivo_b64': documento[2],
            'signer_rut': documento[3],
            'signer_role': documento[4],
            'signer_institucion': documento[5],
            'signer_name': documento[6],
            'signer_email': documento[7],
            'signer_type': documento[8]
        }
        for documento in documentos
    ]
    return documentos

def get_firmantes_by_documento_id(documento_id: int):
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT * FROM firmantes WHERE documento_id = ?
    ''', (documento_id,))
    firmantes = cursor.fetchall()
    firmantes = [
        {
            'id': firmante[0],
            'signer_rut': firmante[1],
            'signer_role': firmante[2],
            'signer_institucion': firmante[3],
            'signer_name': firmante[4],
            'signer_email': firmante[5],
            'signer_type': firmante[6],
            'documento_id': firmante[7]
        }
        for firmante in firmantes
    ]
    return firmantes

def login_user(user_rut: str, user_password: str):
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT * FROM users WHERE rut = ? AND password = ?
    ''', (user_rut, user_password))
    user = cursor.fetchone()
    
    #Genera un Hash para usar de session_id hace el import abajo de lo que requieras:
    session_id = hashlib.sha256(f"{user_rut}{time.time()}".encode()).hexdigest()
    expiration_timestamp = int(time.time()) + 3600
    insert_session(session_id, expiration_timestamp, user_rut)

    if user:
        user = {
            'id': user[0],
            'rut': user[1],
            'username': user[2],
            'email': user[3],
            'session_id': session_id
        }
    else:
        user = {'msg': 'Usuario no encontrado', 'status': 'ERROR'}
    connection.close()


    return user

def insert_session(session_id: str, expiration_timestamp: int, user_rut: str):
    conn = sqlite3.connect('database.sqlite')
    cursor = conn.cursor()

    cursor.execute("INSERT INTO sessions (session_id, expiration_timestamp,user_rut) VALUES (?, ?, ?)",
                   (session_id, expiration_timestamp,user_rut))

    conn.commit()
    conn.close()

def get_session_expiration_timestamp(session_id: str) -> int:
    conn = sqlite3.connect('database.sqlite')
    cursor = conn.cursor()

    cursor.execute("SELECT expiration_timestamp FROM sessions WHERE session_id = ?", (session_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    else:
        return None

def delete_session(session_id: str):
    conn = sqlite3.connect('database.sqlite')
    cursor = conn.cursor()

    cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))

    conn.commit()
    conn.close()


def get_users_by_institucion(institucion_id: int):
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT u.username, u.rut,  u.email, uir.role
        FROM users_institucion_roles uir
        JOIN users u ON uir.user_id = u.id
        WHERE uir.institucion_id = ?
    ''', (institucion_id,))
    usuarios = cursor.fetchall()
    users = {
        'admin': [],
        'trabajador': []
    }
    for user in usuarios:
        if user[3] == 'admin':
            users['admin'].append({
                'username': user[0],
                'rut': user[1],
                'email': user[2]
            })
        elif user[3] == 'trabajador':
            users['trabajador'].append({
                'username': user[0],
                'rut': user[1],
                'email': user[2]
            })
    return users

#funcion para desencriptar la session id y obtener el user_rut de la session_id:
def get_user_rut_by_session_id(session_id: str):
    conn = sqlite3.connect('database.sqlite')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT user_rut FROM sessions WHERE session_id = ? AND expiration_timestamp > ?
    ''', (session_id, int(time.time())))
    user_rut = cursor.fetchone()
    conn.close()
    if user_rut:
        return user_rut[0]


def sign_document(document_id: int):
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    # Actualizar el estado del documento a 'firmado'
    #cursor.execute('''
    #    UPDATE documentos
    #    SET estado = 'Firmado'
    #    WHERE id = ?
    #''', (document_id,))
    #connection.commit()
    #connection.close()

def reject_document(document_id: int):
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    # Actualizar el estado del documento a 'rechazado'
    cursor.execute('''
        UPDATE documentos
        SET estado = 'Declinado'
        WHERE id = ?
    ''', (document_id,))
    connection.commit()
    connection.close()

def create_audit_entry(audit_hash: str, document_id: int, rut_user: str, role: str, tipo_accion: int):
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    #Validar que el documento no haya sido firmado previamente por este usuario:
    cursor.execute('''
        SELECT 1 FROM firmantes WHERE documento_id = ? AND signer_rut = ? AND signer_role = ? AND habilitado = 1
    ''', (document_id, rut_user, role))
    firmante = cursor.fetchone()
    if not firmante:
        return False
    # Crear una entrada de auditoría para el documento firmado
    query = cursor.execute('''
        UPDATE firmantes
        SET audit = ?, fecha_firma = ?, tipo_accion = ?, habilitado = ?
        WHERE documento_id = ? AND signer_rut = ? AND signer_role = ?
    ''', (audit_hash, datetime.now(), tipo_accion, 0, document_id, rut_user, role,))
    connection.commit()
    connection.close()
    #Valida si se hizo o no:
    if query.rowcount == 0:
        return False
    return True

def log_action(user_id: int, action: str, document_id: int):
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    # Registrar la acción en el registro de cambios
    cursor.execute('''
        INSERT INTO registro_cambios (user_id, accion, document_id, fecha)
        VALUES (?, ?, ?, ?)
    ''', (user_id, action, document_id, datetime.now()))
    connection.commit()
    connection.close()

def get_firmantes():
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM firmantes')
    firmantes = cursor.fetchall()
    # añadir key al value retornado
    firmantes = [
        {
            'id': firmante[0],
            'signer_rut': firmante[1],
            'signer_role': firmante[2],
            'signer_institucion': firmante[3],
            'signer_name': firmante[4],
            'signer_email': firmante[5],
            'signer_type': firmante[6],
            'documento_id': firmante[7],
            'audit': firmante[8],
            'fecha_firma': firmante[9],
            'habilitado': firmante[10]
        }
        for firmante in firmantes
    ]
    connection.close()
    return firmantes


#Validar user_password y user_rut en la base de datos:
def validate_user(user_rut: str, user_password: str):
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT * FROM users WHERE rut = ? AND password = ?
    ''', (user_rut, user_password))
    user = cursor.fetchone()
    if user:
        r = True
    else:
        r = False
    connection.close()
    return r