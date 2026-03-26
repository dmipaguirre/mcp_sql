import mysql.connector

# Tus credenciales exactas de Workbench
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",           # Cambia por tu usuario
    "password": "****", # Cambia por tu contraseña
    "database": "Prueba" # Cambia por tu BD
}

def probar_conexion():
    print("⏳ Intentando conectar a MySQL...")
    try:
        # Intentamos abrir la conexión
        conexion = mysql.connector.connect(**DB_CONFIG)
        
        # Verificamos si realmente estamos conectados
        if conexion.is_connected():
            print("\n✅ ¡ÉXITO! Conexión establecida correctamente.")
            
            # Pedimos un dato al servidor para confirmar que responde
            info_servidor = conexion.get_server_info()
            print(f"📦 Versión del servidor MySQL: {info_servidor}")
            
            # Cerramos la conexión (buena práctica)
            conexion.close()
            print("🔒 Conexión cerrada correctamente.")

    except mysql.connector.Error as err:
        # Si algo falla, este bloque captura el error y te lo explica
        print(f"\n❌ ERROR DE CONEXIÓN:")
        if err.errno == 1045:
            print("Problema: Usuario o contraseña incorrectos.")
        elif err.errno == 2003:
            print("Problema: No se puede conectar al servidor. ¿Está encendido MySQL?")
        elif err.errno == 1049:
            print(f"Problema: La base de datos '{DB_CONFIG['database']}' no existe.")
        else:
            print(f"Detalle técnico: {err}")

if __name__ == "__main__":
    probar_conexion()