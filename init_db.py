import sqlite3
import os

def init_db():
    db_path = 'ControlResidencial.db'
    
    # Eliminar BD existente para recrearla limpia si se desea
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 2. TABLA DE ROLES
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Roles (
        id_rol INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_rol VARCHAR(20) NOT NULL
    )
    ''')

    cursor.execute("INSERT INTO Roles (nombre_rol) VALUES ('DIRECTIVA'), ('VECINO')")

    # 3. TABLA PRINCIPAL DE VECINOS
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Vecinos (
        id_vecino INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre VARCHAR(150) NOT NULL,
        dpi VARCHAR(25) UNIQUE NOT NULL,
        numero_lote VARCHAR(50) NOT NULL,
        telefono VARCHAR(20),
        correo_electronico VARCHAR(100),
        status INTEGER NOT NULL DEFAULT 0,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # 4. TABLA DE USUARIOS Y LOGUEO
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Usuarios (
        id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(50) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        id_rol INTEGER,
        id_vecino_vinculado INTEGER NULL,
        FOREIGN KEY (id_rol) REFERENCES Roles(id_rol),
        FOREIGN KEY (id_vecino_vinculado) REFERENCES Vecinos(id_vecino) ON DELETE CASCADE
    )
    ''')

    # 6. INSERCIÓN DE DATOS INICIALES
    vecinos_data = [
        ('NATAN RODAS', '30', '2317', '31001708', 1),
        ('ALVARO TRUJILLO', '60', '1234', '55456655', 0),
        ('WILLIAM ARREAGA', '90', '77766', '88877788', 1)
    ]
    cursor.executemany('''
    INSERT INTO Vecinos (nombre, numero_lote, dpi, telefono, status) 
    VALUES (?, ?, ?, ?, ?)
    ''', vecinos_data)

    # 7. CREACIÓN DE USUARIOS DE PRUEBA
    usuarios_data = [
        ('admin_delco', 'clave_maestra_2026', 1, None),
        ('NIR', 'M2026', 1, None),
        ('sisdel', 'm2026', 1, None),
        ('vecino30', 'lote30', 2, 1)
    ]
    cursor.executemany('''
    INSERT INTO Usuarios (username, password_hash, id_rol, id_vecino_vinculado) 
    VALUES (?, ?, ?, ?)
    ''', usuarios_data)

    conn.commit()
    conn.close()
    
    print("Base de datos SQLite generada exitosamente en 'ControlResidencial.db'.")
    print("Usuarios de prueba creados:")
    print(" - Admin: admin_delco / clave_maestra_2026")
    print(" - Vecino: vecino30 / lote30")

if __name__ == '__main__':
    init_db()
