import sqlite3
import os

# Ruta base
DB_DIR = 'database'
os.makedirs(DB_DIR, exist_ok=True)

# Crear base de datos de tela
def crear_base_tela():
    conn = sqlite3.connect(f'{DB_DIR}/tela.db')
    c = conn.cursor()

    # Secciones institucionales
    c.execute('''
        CREATE TABLE IF NOT EXISTS secciones (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL
        )
    ''')

    # Productos sin cantidad directa — se gestiona por ubicación
    c.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            seccion_id INTEGER,
            FOREIGN KEY(seccion_id) REFERENCES secciones(id)
        )
    ''')

    # Stock en local
    c.execute('''
        CREATE TABLE IF NOT EXISTS stock_local (
            producto_id INTEGER PRIMARY KEY,
            cantidad INTEGER DEFAULT 0,
            FOREIGN KEY(producto_id) REFERENCES productos(id)
        )
    ''')

    # Stock en taller
    c.execute('''
        CREATE TABLE IF NOT EXISTS stock_taller (
            producto_id INTEGER PRIMARY KEY,
            cantidad INTEGER DEFAULT 0,
            FOREIGN KEY(producto_id) REFERENCES productos(id)
        )
    ''')

    conn.commit()
    conn.close()

def crear_base_madera():
    conn = sqlite3.connect(f'{DB_DIR}/madera.db')
    c = conn.cursor()

    # Secciones institucionales
    c.execute('''
        CREATE TABLE IF NOT EXISTS secciones (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL
        )
    ''')

    # Productos sin cantidad directa — se gestiona por ubicación
    c.execute('''
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY,
            nombre TEXT NOT NULL,
            seccion_id INTEGER,
            FOREIGN KEY(seccion_id) REFERENCES secciones(id)
        )
    ''')

    # Stock en local
    c.execute('''
        CREATE TABLE IF NOT EXISTS stock_local (
            producto_id INTEGER PRIMARY KEY,
            cantidad INTEGER DEFAULT 0,
            FOREIGN KEY(producto_id) REFERENCES productos(id)
        )
    ''')

    # Stock en taller
    c.execute('''
        CREATE TABLE IF NOT EXISTS stock_taller (
            producto_id INTEGER PRIMARY KEY,
            cantidad INTEGER DEFAULT 0,
            FOREIGN KEY(producto_id) REFERENCES productos(id)
        )
    ''')

    conn.commit()
    conn.close()


# Ejecutar cuando querés inicializar
def inicializar_bases():
    crear_base_tela()
    crear_base_madera()


