import sqlite3

def initialize_database():
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor() #Creo un cursor
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
            rut_admin TEXT NOT NULL);
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
    connection.commit() # Lanzo la accion
    connection.close() # cierro la conexion

def create_user(username: str, rut: str, email: str, password: str):
    connection = sqlite3.connect('database.sqlite')
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO users(username, rut, email, password)
        VALUES(?, ?, ?, ?)
    ''', (username, rut, email, password))
    #cuando se cree un usuario, debe crearse una institucion personal para el usuario se dejara logo por defecto.
    cursor.execute('''
        INSERT INTO institucion(institucion, url_logo, rut_admin)
        VALUES(?, ?, ?)
    ''', (username, None, rut))
    
    connection.commit()
    connection.close()

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
            'institucion': role[2],
            'role': role[3]
        }
        for role in roles
    ] 