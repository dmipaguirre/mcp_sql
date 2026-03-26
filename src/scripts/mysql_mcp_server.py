from mcp.server.fastmcp import FastMCP
import mysql.connector
import os
from dotenv import load_dotenv

# 1. Inicializamos el servidor MCP
mcp = FastMCP("Servidor_MySQL_Local")

# 2. Configura tus credenciales de MySQL
load_dotenv()

DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": os.getenv("DB_PASSWORD"),
    "database": "prueba"
}

def obtener_conexion():
    return mysql.connector.connect(**DB_CONFIG)

# 3. Creamos una herramienta (Tool) que el modelo local podrá ejecutar
# --- HERRAMIENTA 1: SOLO LECTURA ---
@mcp.tool()
def leer_datos_mysql(query: str) -> str:
    """
    Usa esta herramienta SOLO para leer datos o ver la estructura.
    Ejecuta consultas SELECT, SHOW TABLES, DESCRIBE, etc.
    NO uses esta herramienta para insertar o crear tablas.
    """
    try:
        if not query.strip().upper().startswith(("SELECT", "SHOW", "DESCRIBE", "EXPLAIN")):
            return "Error: Esta herramienta es solo para lectura. Usa 'modificar_base_datos' para otras acciones."

        conn = obtener_conexion()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        resultados = cursor.fetchall()
        conn.close()
        
        return str(resultados) if resultados else "La consulta se ejecutó sin errores, pero está vacía."
    
    except Exception as e:
        return f"Error en lectura: {e}"

# --- HERRAMIENTA 2: ESCRITURA Y MODIFICACIÓN ---
@mcp.tool()
def modificar_base_datos(query: str) -> str:
    """
    Usa esta herramienta para MODIFICAR la base de datos.
    Permite comandos como CREATE TABLE, INSERT, UPDATE, DELETE, ALTER o DROP.
    """
    try:
        # Prevenir que use esta herramienta solo para leer (buenas prácticas para el modelo)
        if query.strip().upper().startswith(("SELECT", "SHOW", "DESCRIBE")):
            return "Aviso: Estás intentando leer datos. Por favor, usa la herramienta 'leer_datos_mysql' para esto."

        conn = obtener_conexion()
        cursor = conn.cursor()
        cursor.execute(query)
        
        conn.commit() 
        
        filas_afectadas = cursor.rowcount
        conn.close()
        
        return f"Éxito. La operación se realizó correctamente. Filas afectadas/creadas: {filas_afectadas}"
    
    except mysql.connector.Error as err:
        return f"Error de MySQL al modificar: {err}"
    except Exception as e:
        return f"Error inesperado al modificar: {e}"

if __name__ == "__main__":
    # Inicia el servidor MCP usando STDIO (estándar para clientes MCP)
    mcp.run()