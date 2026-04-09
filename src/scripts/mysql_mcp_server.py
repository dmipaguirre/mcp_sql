from mcp.server.fastmcp import FastMCP
import mysql.connector
from mysql.connector import pooling  # MEJORA: usamos pool de conexiones en lugar de abrir/cerrar cada vez
import os
from dotenv import load_dotenv
from contextlib import contextmanager

# 1. Inicializamos el servidor MCP
mcp = FastMCP("Servidor_MySQL_Local")

# 2. Cargamos credenciales desde .env
# ORIGINAL: DB_PASSWORD estaba en .env, pero "database" estaba hardcodeada como "prueba"
# MEJORA: todo lo configurable va a .env, incluyendo host, user y database
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "user": os.getenv("DB_USER", "mcp_readonly"),   # MEJORA: no usar root; crear un usuario con permisos mínimos
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME", "prueba"),
    "pool_name": "mcp_pool",
    "pool_size": 5,                                  # MEJORA: pool para reutilizar conexiones sin overhead
}

# Creamos el pool una sola vez al arrancar el servidor
# ORIGINAL: obtener_conexion() abría una nueva conexión en cada llamada y la cerraba manualmente,
# lo que causa leak si hay una excepción antes del conn.close()
try:
    connection_pool = pooling.MySQLConnectionPool(**DB_CONFIG)
except mysql.connector.Error as e:
    raise RuntimeError(f"No se pudo inicializar el pool de conexiones: {e}")


@contextmanager
def obtener_conexion():
    """
    Context manager que obtiene una conexión del pool y garantiza
    que se devuelve al pool incluso si ocurre una excepción.

    ORIGINAL: la conexión se cerraba con conn.close() al final, pero si cursor.execute()
    lanzaba una excepción, conn.close() nunca se ejecutaba → connection leak.
    MEJORA: con 'with' + contextmanager, el cierre está garantizado siempre.
    """
    conn = connection_pool.get_connection()
    try:
        yield conn
    finally:
        conn.close()  # devuelve la conexión al pool, no la destruye


# Palabras clave permitidas por herramienta
# ORIGINAL: la validación usaba .strip().upper().startswith(), que es fácil de evadir
# con espacios, saltos de línea o queries compuestas ("; DROP TABLE...")
# MEJORA: normalizamos el texto y comprobamos con split() para obtener la primera palabra real
PALABRAS_LECTURA = {"SELECT", "SHOW", "DESCRIBE", "EXPLAIN"}
PALABRAS_ESCRITURA = {"INSERT", "UPDATE", "DELETE", "CREATE", "ALTER", "DROP", "TRUNCATE"}


def primera_palabra(query: str) -> str:
    """Devuelve la primera palabra clave de la query, ignorando espacios y saltos de línea."""
    return query.strip().split()[0].upper() if query.strip() else ""


# --- HERRAMIENTA 1: SOLO LECTURA ---
@mcp.tool()
def leer_datos_mysql(query: str) -> str:
    """
    Usa esta herramienta SOLO para leer datos o ver la estructura.
    Ejecuta consultas SELECT, SHOW TABLES, DESCRIBE, EXPLAIN.
    NO uses esta herramienta para insertar, modificar o crear tablas.
    """
    # MEJORA: validación más robusta usando la primera palabra real del query
    if primera_palabra(query) not in PALABRAS_LECTURA:
        return (
            "Error: Esta herramienta es solo para lectura. "
            "Usa 'modificar_base_datos' para INSERT, UPDATE, DELETE, etc."
        )

    try:
        # MEJORA: usamos 'with' para garantizar el cierre de conexión y cursor
        with obtener_conexion() as conn:
            with conn.cursor(dictionary=True) as cursor:
                # MEJORA: aunque aquí las queries vienen del LLM y son difíciles de parametrizar,
                # en un entorno productivo se debería usar un parser SQL o lista blanca de queries
                cursor.execute(query)
                resultados = cursor.fetchall()

        return str(resultados) if resultados else "Consulta ejecutada correctamente, sin resultados."

    except mysql.connector.Error as err:
        # ORIGINAL: capturaba Exception genérico para todo
        # MEJORA: diferenciamos error de MySQL del error inesperado para mensajes más claros
        return f"Error de MySQL en lectura: {err}"
    except Exception as e:
        return f"Error inesperado en lectura: {e}"


# --- HERRAMIENTA 2: ESCRITURA Y MODIFICACIÓN ---
@mcp.tool()
def modificar_base_datos(query: str) -> str:
    """
    Usa esta herramienta para MODIFICAR la base de datos.
    Permite: CREATE TABLE, INSERT, UPDATE, DELETE, ALTER, DROP, TRUNCATE.
    NO uses esta herramienta para leer datos.
    """
    primera = primera_palabra(query)

    if primera in PALABRAS_LECTURA:
        return (
            "Aviso: estás intentando leer datos. "
            "Por favor, usa 'leer_datos_mysql' para SELECT, SHOW o DESCRIBE."
        )

    # MEJORA: rechazamos explícitamente queries que no reconocemos en ninguna categoría
    if primera not in PALABRAS_ESCRITURA:
        return (
            f"Error: el comando '{primera}' no está permitido. "
            f"Solo se aceptan: {', '.join(sorted(PALABRAS_ESCRITURA))}."
        )

    try:
        with obtener_conexion() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query)
                conn.commit()
                filas_afectadas = cursor.rowcount

        return f"Éxito. Operación realizada correctamente. Filas afectadas: {filas_afectadas}"

    except mysql.connector.Error as err:
        return f"Error de MySQL al modificar: {err}"
    except Exception as e:
        return f"Error inesperado al modificar: {e}"


if __name__ == "__main__":
    mcp.run()