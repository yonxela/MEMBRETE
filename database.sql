-- 1. CREACIÓN DE LA BASE DE DATOS Y SEGURIDAD MÍNIMA
CREATE DATABASE IF NOT EXISTS ControlResidencial_Delco;
USE ControlResidencial_Delco;

-- 2. TABLA DE ROLES (Para el Formulario de Ingreso)
CREATE TABLE Roles (
    id_rol INT PRIMARY KEY AUTO_INCREMENT,
    nombre_rol VARCHAR(20) NOT NULL -- 'DIRECTIVA' o 'VECINO'
);

INSERT INTO Roles (nombre_rol) VALUES ('DIRECTIVA'), ('VECINO');

-- 3. TABLA PRINCIPAL DE VECINOS (Módulo de Registro)
-- Incluye todos los datos solicitados: Nombre, DPI, Lote, Teléfono y Status
CREATE TABLE Vecinos (
    id_vecino INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(150) NOT NULL,
    dpi VARCHAR(25) UNIQUE NOT NULL, -- Clave única para evitar duplicados
    numero_lote VARCHAR(50) NOT NULL,
    telefono VARCHAR(20),
    correo_electronico VARCHAR(100),
    status TINYINT(1) NOT NULL DEFAULT 0, -- 1: Pagos al día (Verde), 0: No ha pagado (Rojo)
    dias_demora INT NOT NULL DEFAULT 0, -- Agregado para cobros y restriccion
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. TABLA DE USUARIOS Y LOGUEO (Punto 3 del requerimiento)
-- Permite que la directiva vea todo y el vecino solo lo suyo
CREATE TABLE Usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, -- Almacenar siempre encriptado
    id_rol INT,
    id_vecino_vinculado INT NULL, -- Solo se llena si el rol es 'VECINO'
    FOREIGN KEY (id_rol) REFERENCES Roles(id_rol),
    FOREIGN KEY (id_vecino_vinculado) REFERENCES Vecinos(id_vecino) ON DELETE CASCADE
);

-- 5. TABLA DE AUDITORÍA DE PAGOS (Idea adicional experta)
-- Para llevar un registro de cuándo cambió el status de un vecino
CREATE TABLE Historial_Status (
    id_log INT PRIMARY KEY AUTO_INCREMENT,
    id_vecino INT,
    status_anterior TINYINT(1),
    nuevo_status TINYINT(1),
    fecha_cambio DATETIME DEFAULT CURRENT_TIMESTAMP,
    modificado_por INT, -- ID del usuario de la directiva que hizo el cambio
    FOREIGN KEY (id_vecino) REFERENCES Vecinos(id_vecino),
    FOREIGN KEY (modificado_por) REFERENCES Usuarios(id_usuario)
);

-- 6. INSERCIÓN DE DATOS INICIALES (BASADO EN TU EXCEL)
INSERT INTO Vecinos (nombre, numero_lote, dpi, telefono, status, dias_demora) VALUES 
('NATAN RODAS', '30', '2317', '31001708', 1, 0),
('ALVARO TRUJILLO', '60', '1234', '55456655', 0, 30),
('WILLIAM ARREAGA', '90', '77766', '88877788', 1, 0);

-- 7. CREACIÓN DE USUARIOS DE PRUEBA
-- Usuario Directiva (Acceso Total)
INSERT INTO Usuarios (username, password_hash, id_rol) 
VALUES ('admin_delco', 'clave_maestra_2026', 1);

-- Usuario Vecino (Acceso solo a su estatus)
INSERT INTO Usuarios (username, password_hash, id_rol, id_vecino_vinculado) 
VALUES ('vecino30', 'lote30', 2, 1);

-- Vistas Especializadas para los Marbetes
CREATE VIEW Vista_Marbetes AS
SELECT nombre, numero_lote, 
       IF(status = 1, 'VERDE', 'ROJO') AS color_franja,
       IF(status = 1, 'PAGOS AL DIA', 'NO HA PAGADO') AS texto_franja
FROM Vecinos;

-- 8. TABLA DE MENSAJES (Bandeja de Entrada / Comunicados)
CREATE TABLE Mensajes (
    id_mensaje INT PRIMARY KEY AUTO_INCREMENT,
    id_remitente INT NOT NULL, -- Usuario que envía el mensaje (ej. Directiva)
    id_destinatario INT NOT NULL, -- Usuario que recibe (Vecino u otro admin)
    asunto VARCHAR(150) NOT NULL,
    cuerpo TEXT NOT NULL,
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    leido TINYINT(1) DEFAULT 0, -- 0: No leido, 1: Leido
    FOREIGN KEY (id_remitente) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE,
    FOREIGN KEY (id_destinatario) REFERENCES Usuarios(id_usuario) ON DELETE CASCADE
);
