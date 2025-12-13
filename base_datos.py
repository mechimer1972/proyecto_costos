import sys, os
import sqlite3
from datetime import datetime

# Detecta la carpeta base correctamente incluso dentro del exe
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RUTA_DB = os.path.join(BASE_DIR, "bd_costos.db")
RUTA_HISTORIAL = os.path.join(BASE_DIR, "historial_modificaciones.txt")

print("📁 Usando base de datos:", RUTA_DB)

def registrar_modificacion(nombre, precio_anterior, precio_nuevo):
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    with open(RUTA_HISTORIAL, "a", encoding="utf-8") as archivo:
        archivo.write(f"{fecha},{nombre},{precio_anterior},{precio_nuevo}\n")

def conectar():
    conn = sqlite3.connect(RUTA_DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materias_primas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            precio REAL NOT NULL,
            proveedor TEXT,
            fecha TEXT NOT NULL
        )
    """)
    conn.commit()
    return conn



def guardar_materia_prima(nombre, categoria, precio, proveedor):
    conn = conectar()
    cursor = conn.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
        INSERT INTO materias_primas (nombre, categoria, precio, proveedor, fecha)
        VALUES (?, ?, ?, ?, ?)
    """, (nombre, categoria, precio, proveedor, fecha))

    conn.commit()
    conn.close()


def guardar_materia_prima_debug(nombre, categoria, precio, proveedor=""):
    print("➡️ Llamado a guardar_materia_prima con:", nombre, categoria, precio, proveedor)

    try:
        conn = conectar()
        cursor = conn.cursor()
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute("""
            INSERT INTO materias_primas (nombre, categoria, precio, proveedor, fecha)
            VALUES (?, ?, ?, ?, ?)
        """, (nombre, categoria, precio, proveedor, fecha))

        conn.commit()

        # mostrar última fila insertada
        cursor.execute("""
            SELECT id, nombre, categoria, precio, proveedor, fecha
            FROM materias_primas
            ORDER BY id DESC LIMIT 1
        """)
        fila = cursor.fetchone()
        print("✅ Insertado:", fila)
        return True

    except Exception as e:
        print("❌ Error guardando materia prima:", e)
        return False

    finally:
        conn.close()


def modificar_materia(nombre, nueva_categoria, nuevo_precio, proveedor):
    conn = sqlite3.connect(RUTA_DB)
    cursor = conn.cursor()

    # Actualizar precio, categoría y proveedor
    cursor.execute("""
        UPDATE materias_primas
        SET categoria = ?, precio = ?, proveedor = ?
        WHERE nombre = ?
    """, (nueva_categoria, float(nuevo_precio), proveedor, nombre))

    # Buscar recetas que usan esta materia prima
    cursor.execute("SELECT id_receta FROM ingredientes WHERE nombre_materia=?", (nombre,))
    recetas_afectadas = cursor.fetchall()

    # Recalcular cada receta
    for (id_receta,) in recetas_afectadas:
        cursor.execute("SELECT nombre_materia, cantidad FROM ingredientes WHERE id_receta=?", (id_receta,))
        ingredientes = cursor.fetchall()

        costo_total = 0
        for nombre_mp, cantidad in ingredientes:
            cursor.execute("SELECT precio FROM materias_primas WHERE nombre=?", (nombre_mp,))
            resultado = cursor.fetchone()
            if resultado:
                precio = resultado[0]
                costo_total += precio * cantidad / 1000  # suponiendo que cantidad está en gramos

        cursor.execute("UPDATE recetas SET costo_total=? WHERE id=?", (costo_total, id_receta))

    conn.commit()
    conn.close()


def recalcular_costos_receta(cursor, id_receta):
    # Obtener todos los ingredientes de la receta
    cursor.execute("SELECT nombre_materia, cantidad FROM ingredientes WHERE id_receta=?", (id_receta,))
    ingredientes = cursor.fetchall()

    costo_total = 0
    for nombre_mp, cantidad in ingredientes:
        cursor.execute("SELECT precio FROM materias_primas WHERE nombre=?", (nombre_mp,))
        resultado = cursor.fetchone()
        if resultado:
            precio = resultado[0]
            costo_total += precio * cantidad / 1000  # suponiendo que cantidad está en gramos

    # Actualizar el costo total de la receta
    cursor.execute("UPDATE recetas SET costo_total=? WHERE id=?", (costo_total, id_receta))


def obtener_materias_primas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nombre, categoria, precio, proveedor, fecha 
        FROM materias_primas
        ORDER BY fecha DESC
    """)
    datos = cursor.fetchall()
    conn.close()
    return datos


def obtener_precio_actual(nombre):
    for mp in obtener_materias_primas():
        if mp[0] == nombre:
            return mp[2]
    return 0.0

import sqlite3
from datetime import datetime

def agregar_receta(nombre, ingredientes, peso_total, merma, peso_final, costo_total,
                   peso_unidad, rinde, envase, costo_unidad):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(RUTA_DB)
    cursor = conn.cursor()

    # ⚠️ Importante: NO volver a sumar el costo del envase aquí,
    # porque ya lo calculás en recetas.py. Si lo sumás dos veces,
    # los valores quedan corridos.
    
    cursor.execute("""
        INSERT INTO recetas (nombre, peso_total, merma, peso_final, costo_total,
                             peso_unidad, rinde, envase, costo_unidad, fecha)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nombre, peso_total, merma, peso_final, costo_total,
          peso_unidad, rinde, envase, costo_unidad, fecha))

    id_receta = cursor.lastrowid
    print("Receta guardada con ID:", id_receta)

    # Insertar ingredientes vinculados al ID de la receta
    for materia, cantidad, costo in ingredientes:
        cursor.execute("""
            INSERT INTO ingredientes_receta (id_receta, materia, cantidad, costo)
            VALUES (?, ?, ?, ?)
        """, (id_receta, materia, cantidad, costo))

    conn.commit()
    conn.close()

def modificar_receta(id_receta, nombre, ingredientes, costo_total):
    ingredientes_str = ",".join([f"{nombre}:{cantidad}" for nombre, cantidad, _ in ingredientes])
    conexion = sqlite3.connect(RUTA_DB)
    cursor = conexion.cursor()
    cursor.execute("UPDATE recetas SET nombre = ?, ingredientes = ?, costo_total = ? WHERE id = ?",
                   (nombre, ingredientes_str, costo_total, id_receta))
    conexion.commit()
    conexion.close()

def guardar_receta(nombre, ingredientes, peso_total, merma, peso_final, costo_total,
                   peso_unidad, rinde, envase, costo_unidad):
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(RUTA_DB)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO recetas (nombre, peso_total, merma, peso_final, costo_total,
                             peso_unidad, rinde, envase, costo_unidad, fecha)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (nombre, peso_total, merma, peso_final, costo_total,
          peso_unidad, rinde, envase, costo_unidad, fecha))

    id_receta = cursor.lastrowid

    for materia, cantidad, costo in ingredientes:
        cursor.execute("""
            INSERT INTO ingredientes_receta (id_receta, materia, cantidad, costo)
            VALUES (?, ?, ?, ?)
        """, (id_receta, materia, cantidad, costo))

    conn.commit()
    conn.close()


def eliminar_receta(id_receta):
    conn = sqlite3.connect(RUTA_DB)
    cursor = conn.cursor()

    # Primero eliminar ingredientes de la receta
    cursor.execute("DELETE FROM ingredientes_receta WHERE id_receta = ?", (id_receta,))

    # Luego eliminar la receta
    cursor.execute("DELETE FROM recetas WHERE id = ?", (id_receta,))

    conn.commit()
    conn.close()


def obtener_recetas():
    conn = sqlite3.connect(RUTA_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM recetas ORDER BY id DESC")
    recetas = cursor.fetchall()
    conn.close()
    return recetas

def obtener_conformacion_receta(nombre_receta):
    import sqlite3
    conn = sqlite3.connect(RUTA_DB)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM recetas WHERE nombre = ?", (nombre_receta,))
    resultado = cursor.fetchone()
    if not resultado:
        conn.close()
        return []

    id_receta = resultado[0]

    cursor.execute("""
        SELECT materia, cantidad, costo
        FROM ingredientes_receta
        WHERE id_receta = ?
    """, (id_receta,))
    ingredientes = cursor.fetchall()
    conn.close()
    return ingredientes



def obtener_envases():
    import sqlite3
    conn = sqlite3.connect(RUTA_DB)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM materias_primas WHERE categoria = 'Envases'")
    envases = [fila[0] for fila in cursor.fetchall()]
    conn.close()
    return envases

def eliminar_materia(nombre):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM materias_primas WHERE nombre = ?", (nombre,))
    conn.commit()
    conn.close()

def modificar_materia(nombre, nueva_categoria, nuevo_precio):
    conn = sqlite3.connect(RUTA_DB)
    cursor = conn.cursor()


    # Actualizar el precio y categoría
    cursor.execute("UPDATE materias_primas SET categoria=?, precio=? WHERE nombre=?", (nueva_categoria, nuevo_precio, nombre))

    # Buscar recetas que usan esta materia prima
    cursor.execute("SELECT id_receta FROM ingredientes_receta WHERE materia=?", (nombre,))
    recetas_afectadas = cursor.fetchall()

    # Recalcular cada receta
    for (id_receta,) in recetas_afectadas:
        cursor.execute("SELECT materia, cantidad FROM ingredientes_receta WHERE id_receta=?", (id_receta,))
        ingredientes = cursor.fetchall()

        costo_total = 0
        for nombre_mp, cantidad in ingredientes:
            cursor.execute("SELECT precio FROM materias_primas WHERE nombre=?", (nombre_mp,))
            resultado = cursor.fetchone()
            if resultado:
                precio = resultado[0]
                costo_total += precio * cantidad / 1000  # suponiendo que cantidad está en gramos

        cursor.execute("UPDATE recetas SET costo_total=? WHERE id=?", (costo_total, id_receta))

    conn.commit()
    conn.close()

print(obtener_materias_primas())

def crear_tablas_recetas():
    conn = sqlite3.connect(RUTA_DB)
    cursor = conn.cursor()

    # Tabla principal de recetas
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS recetas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            peso_total REAL,
            merma REAL,
            peso_final REAL,
            costo_total REAL,
            peso_unidad REAL,
            rinde REAL,
            envase TEXT,
            costo_unidad REAL,
            fecha TEXT
        )
    """)

    # Tabla de ingredientes por receta
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ingredientes_receta (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            id_receta INTEGER,
            materia TEXT,
            cantidad REAL,
            costo REAL,
            FOREIGN KEY (id_receta) REFERENCES recetas(id)
        )
    """)

    conn.commit()
    conn.close()

    def modificar_receta(id_receta, nuevos_datos):
        conn = sqlite3.connect(RUTA_DB)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE recetas
            SET nombre = ?, merma = ?, peso_unidad = ?, envase = ?
            WHERE id = ?
        """, (
            nuevos_datos["nombre"],
            nuevos_datos["merma"],
            nuevos_datos["peso_unidad"],
            nuevos_datos["envase"],
            id_receta
        ))
        conn.commit()
        conn.close()

def actualizar_costos_por_materia(nombre_materia):
    """
    Recalcula los costos de todas las recetas que usan una materia prima cuyo precio cambió.
    """
    conn = sqlite3.connect(RUTA_DB)
    cursor = conn.cursor()

    # 1️⃣ Obtener el nuevo precio por kg de la materia prima
    cursor.execute("SELECT precio FROM materias_primas WHERE nombre = ?", (nombre_materia,))
    resultado = cursor.fetchone()
    if not resultado:
        conn.close()
        return
    nuevo_precio = resultado[0]

    # 2️⃣ Buscar todos los ingredientes donde se usa esa materia prima
    cursor.execute("""
        SELECT id_receta, cantidad
        FROM ingredientes_receta
        WHERE materia = ?
    """, (nombre_materia,))
    ingredientes = cursor.fetchall()

    for id_receta, cantidad in ingredientes:
        # 3️⃣ Calcular nuevo costo del ingrediente (cantidad en gramos)
        nuevo_costo = (cantidad / 1000) * nuevo_precio

        # 4️⃣ Actualizar el costo del ingrediente
        cursor.execute("""
            UPDATE ingredientes_receta
            SET costo = ?
            WHERE id_receta = ? AND materia = ?
        """, (nuevo_costo, id_receta, nombre_materia))

        # 5️⃣ Sumar todos los costos de ingredientes
        cursor.execute("SELECT SUM(costo) FROM ingredientes_receta WHERE id_receta = ?", (id_receta,))
        total_receta = cursor.fetchone()[0] or 0

        # 6️⃣ Obtener datos de la receta para calcular rinde
        cursor.execute("SELECT peso_final, peso_unidad, envase FROM recetas WHERE id = ?", (id_receta,))
        r = cursor.fetchone()
        peso_final = r[0] if r and r[0] else 0.0

        # Si viene mayor a 50, asumimos que está en GRAMOS (nunca tendrás una receta de 80 kg)
        peso_final_kg = peso_final / 1000.0 if peso_final > 50 else peso_final

        peso_unidad_g = r[1] if r and r[1] else 0.0
        envase = r[2] if r and r[2] else None

        # 7️⃣ Calcular rinde
        rinde = peso_final_kg / (peso_unidad_g / 1000.0) if peso_unidad_g else 0.0

        # 8️⃣ Obtener precio del envase si existe
        costo_envase = 0.0
        if envase:
            cursor.execute("SELECT precio FROM materias_primas WHERE nombre = ?", (envase,))
            resultado_envase = cursor.fetchone()
            if resultado_envase and resultado_envase[0]:
                costo_envase = resultado_envase[0]

        # 9️⃣ Calcular costo por unidad incluyendo envase
        costo_unidad = (total_receta / rinde) + costo_envase if rinde else 0.0

        #  🔟 Actualizar en la BD
        cursor.execute("""
    UPDATE recetas
    SET costo_total = ?, costo_unidad = ?
    WHERE id = ?
""", (total_receta + costo_envase, costo_unidad, id_receta))


    conn.commit()
    conn.close()

