# Tutorial: Cómo funciona este proyecto (paso a paso)

## ¿Qué es este proyecto?

Este proyecto conecta un modelo de inteligencia artificial local (Ollama) con una base de datos MySQL, permitiendo que el modelo pueda leer y modificar la base de datos mediante conversaciones en lenguaje natural.

---

## Estructura del proyecto

El proyecto está organizado de la siguiente manera:

```
/                               # Raíz del repositorio
│
├─ src/
│   └─ scripts/                 # Código fuente principal
│       ├─ mysql_mcp_server.py  # Servidor MCP y herramientas
│       └─ cliente_mcp.py       # Cliente que habla con Ollama
│
├─ tests/                       # Tests y scripts de prueba
│   └─ prueba_conexion.py
│
├─ docs/                        # Documentación adicional
│   └─ tutorial.md
│
├─ .env                         # Variables de entorno
├─ .gitignore
├─ opencode.jsonc
├─ pyproject.toml
├─ uv.lock
└─ README.md
```

### 1. prueba_conexion.py - Verificar que MySQL funciona

```python
import mysql.connector

# Configuración de la base de datos
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "tu_contraseña",
    "database": "tu_base_de_datos"
}

def probar_conexion():
    # Intentamos abrir la conexión
    conexion = mysql.connector.connect(**DB_CONFIG)
    
    # Verificamos si realmente estamos conectados
    if conexion.is_connected():
        print("¡ÉXITO! Conexión establecida correctamente.")
```

**¿Qué hace?**
- Intenta conectarse a MySQL con las credenciales que le des
- Si funciona, muestra un mensaje de éxito
- Si falla, te dice exactamente qué problema tienes (contraseña incorrecta, servidor apagado, base de datos no existe)

**Para ejecutarlo:**
```bash
python scripts/prueba_conexion.py
```

---

### 2. mysql_mcp_server.py - El servidor que conecta Python con MySQL

```python
from mcp.server.fastmcp import FastMCP
import mysql.connector

# 1. Inicializamos el servidor MCP
mcp = FastMCP("Servidor_MySQL_Local")

# 2. Configura tus credenciales de MySQL
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "tu_contraseña",
    "database": "tu_base_de_datos"
}

# Función para obtener una conexión a la base de datos
def obtener_conexion():
    return mysql.connector.connect(**DB_CONFIG)
```

**¿Qué hace este archivo?**

El servidor MCP (Model Context Protocol) es como un "traductor" entre el modelo de IA y la base de datos. Este archivo define dos herramientas (tools):

#### Herramienta 1: leer_datos_mysql
```python
@mcp.tool()
def leer_datos_mysql(query: str) -> str:
    # Solo permite consultas de lectura: SELECT, SHOW, DESCRIBE
    if not query.strip().upper().startswith(("SELECT", "SHOW", "DESCRIBE", "EXPLAIN")):
        return "Error: Esta herramienta es solo para lectura."
    
    conn = obtener_conexion()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(query)
    resultados = cursor.fetchall()
    conn.close()
    
    return str(resultados) if resultados else "La consulta está vacía."
```

**Propósito:** Permite al modelo leer datos de la base de datos (SELECT, ver tablas, describe)

#### Herramienta 2: modificar_base_datos
```python
@mcp.tool()
def modificar_base_datos(query: str) -> str:
    # No permite consultas de lectura (previene errores)
    if query.strip().upper().startswith(("SELECT", "SHOW", "DESCRIBE")):
        return "Usa leer_datos_mysql para esto."
    
    conn = obtener_conexion()
    cursor = conn.cursor()
    cursor.execute(query)
    conn.commit()  # ¡Importante! Confirma los cambios
    filas_afectadas = cursor.rowcount
    conn.close()
    
    return f"Éxito. Filas afectadas: {filas_afectadas}"
```

**Propósito:** Permite crear tablas, insertar datos, actualizar, eliminar

#### Iniciar el servidor
```python
if __name__ == "__main__":
    mcp.run()
```

Esto inicia el servidor MCP que escuchará solicitudes a través de STDIO (entrada/salida estándar).

---

### 3. cliente_mcp.py - El cliente que conecta Ollama con el servidor MCP

```python
import asyncio
from ollama import AsyncClient
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Modelo de Ollama a usar
MODELO = 'qwen3.5:9b'
```

**¿Qué hace este archivo?**

Este es el "puente" entre el modelo de IA y el servidor MCP. Permite que el usuario chattee con la IA y ella pueda ejecutar consultas SQL automáticamente.

#### Paso 1: Configurar el servidor MCP
```python
parametros_servidor = StdioServerParameters(
    command="python",
    args=["src/server/mysql_mcp_server.py"]
)
```

#### Paso 2: Conectar con el servidor
```python
async with stdio_client(parametros_servidor) as (lectura, escritura):
    async with ClientSession(lectura, escritura) as sesion:
        await sesion.initialize()
        
        # Obtener las herramientas disponibles
        mcp_tools = await sesion.list_tools()
```

#### Paso 3: Convertir herramientas al formato de Ollama
```python
ollama_tools = []
for tool in mcp_tools.tools:
    ollama_tools.append({
        "type": "function",
        "function": {
            "name": tool.name,
            "description": tool.description,
            "parameters": tool.inputSchema
        }
    })
```

#### Paso 4: Bucle de chat
```python
while True:
    texto_usuario = input("🗿 Tú: ")
    
    # Enviar mensaje a Ollama con las herramientas disponibles
    respuesta = await cliente_ollama.chat(
        model=MODELO,
        messages=mensajes,
        tools=ollama_tools
    )
```

#### Paso 5: Si Ollama usa una herramienta
```python
if mensaje_ia.get('tool_calls'):
    for tool_call in mensaje_ia['tool_calls']:
        nombre_herramienta = tool_call['function']['name']
        argumentos = tool_call['function']['arguments']
        
        # Ejecutar la herramienta a través del servidor MCP
        resultado_mcp = await sesion.call_tool(nombre_herramienta, argumentos)
        
        # Enviar el resultado de vuelta a Ollama
        mensajes.append({
            "role": "tool",
            "name": nombre_herramienta,
            "content": texto_resultado
        })
    
    # Segunda llamada a Ollama para que procese el resultado
    respuesta_final = await cliente_ollama.chat(
        model=MODELO,
        messages=mensajes
    )
```

---

## Cómo ejecutarlo

### 1. Verificar conexión a MySQL
```bash
python tests/prueba_conexion.py
```

### 2. Iniciar el cliente (el servidor MCP se inicia automáticamente)
```bash
python src/scripts/cliente_mcp.py
```

### 3. Chatear con la IA

Ejemplo de conversación:
- **Tú:** "Muéstrame las tablas que hay en la base de datos"
- **IA:** (ejecuta SHOW TABLES automáticamente)
- **Tú:** "Dame los datos de la tabla usuarios"
- **IA:** (ejecuta SELECT * FROM usuarios)

---

## Requisitos previos

1. **MySQL** instalado y ejecutándose
2. **Ollama** instalado con un modelo descargado (ej: `ollama pull qwen3.5:9b`)
3. **Paquetes Python:**
   ```bash
   pip install mysql-connector-python mcp ollama
   ```

---