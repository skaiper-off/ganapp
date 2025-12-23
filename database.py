import sqlite3
import os

DB_NAME = "ganapp.db"

def conectar():
    """Establece conexión con la base de datos"""
    return sqlite3.connect(DB_NAME)

def crear_tablas():
    """Crea las tablas necesarias si no existen"""
    conn = conectar()
    cursor = conn.cursor()

    # Tabla de ganado
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ganado (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        arete TEXT UNIQUE NOT NULL,
        nombre TEXT,
        sexo TEXT,
        fecha_nacimiento TEXT,
        estado TEXT DEFAULT 'Vivo',
        observaciones TEXT,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Tabla de eventos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS eventos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        arete TEXT NOT NULL,
        tipo TEXT NOT NULL,
        fecha TEXT NOT NULL,
        peso REAL,
        costo REAL,
        notas TEXT,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (arete) REFERENCES ganado(arete) ON DELETE CASCADE
    )
    """)

    # Migración: añadir columnas si no existen
    cursor.execute("PRAGMA table_info(ganado)")
    columnas_ganado = [row[1] for row in cursor.fetchall()]
    
    if 'nombre' not in columnas_ganado:
        cursor.execute("ALTER TABLE ganado ADD COLUMN nombre TEXT")
    
    if 'fecha_registro' not in columnas_ganado:
        cursor.execute("ALTER TABLE ganado ADD COLUMN fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    cursor.execute("PRAGMA table_info(eventos)")
    columnas_eventos = [row[1] for row in cursor.fetchall()]
    
    if 'fecha_registro' not in columnas_eventos:
        cursor.execute("ALTER TABLE eventos ADD COLUMN fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP")

    # Crear índices para mejorar rendimiento
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_ganado_arete ON ganado(arete)
    """)
    
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_eventos_arete ON eventos(arete)
    """)
    
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_eventos_fecha ON eventos(fecha)
    """)

    conn.commit()
    conn.close()

def backup_database(ruta_backup=None):
    """Crea una copia de seguridad de la base de datos"""
    import shutil
    from datetime import datetime
    
    if not ruta_backup:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_backup = f"ganapp_backup_{timestamp}.db"
    
    try:
        shutil.copy2(DB_NAME, ruta_backup)
        return True, f"Backup creado: {ruta_backup}"
    except Exception as e:
        return False, f"Error al crear backup: {str(e)}"

def obtener_estadisticas_rapidas():
    """Obtiene estadísticas rápidas de la base de datos"""
    conn = conectar()
    cursor = conn.cursor()
    
    stats = {}
    
    cursor.execute("SELECT COUNT(*) FROM ganado")
    stats['total_ganado'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM ganado WHERE LOWER(estado) = 'vivo'")
    stats['ganado_vivo'] = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM eventos")
    stats['total_eventos'] = cursor.fetchone()[0]
    
    conn.close()
    return stats

def guardar_evento_pesaje(arete, fecha, peso, notas):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO eventos (arete, tipo, fecha, peso, notas)
        VALUES (?, 'pesaje', ?, ?, ?)
    """, (arete, fecha, peso, notas))

    conn.commit()
    conn.close()

def obtener_eventos():
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT arete, tipo, fecha, peso, notas, fecha_registro
        FROM eventos
        ORDER BY fecha_registro DESC
        LIMIT 20
    """)

    eventos = cursor.fetchall()
    conn.close()
    return eventos

def obtener_eventos_por_arete(arete):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT arete, tipo, fecha, peso, notas, fecha_registro
        FROM eventos
        WHERE arete = ?
        ORDER BY fecha DESC
    """, (arete,))

    eventos = cursor.fetchall()
    conn.close()
    return eventos
