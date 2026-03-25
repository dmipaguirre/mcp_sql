# Detalle del proyecto – Explicación línea por línea

A continuación se describe, con el mayor nivel de detalle posible, qué hace cada línea del código incluido en este repositorio. Los archivos están escritos en Python y utilizan las librerías **mysql‑connector‑python**, **mcp** y **ollama**.

---

## 1. `prueba_conexion.py`

```python
1: import mysql.connector
```
*Importa el driver oficial de MySQL para Python, necesario para abrir conexiones a la base de datos.*

```python
3: # Tus credenciales exactas de Workbench
4: DB_CONFIG = {
5:     "host": "127.0.0.1",
6:     "user": "root",           # Cambia por tu usuario
7:     "password": "********$", # Cambia por tu contraseña
8:     "database": "Prueba" # Cambia por tu BD
9: }
```
*Define un diccionario `DB_CONFIG` con los parámetros que MySQL necesita para conectar: dirección del servidor, usuario, contraseña y base de datos a usar.*

```python
11: def probar_conexion():
```
*Crea la función `probar_conexion`, que encapsula todo el proceso de prueba.*

```python
12:     print("⏳ Intentando conectar a MySQL...")
```
*Mensaje informativo para el usuario antes de intentar la conexión.*

```python
13:     try:
```
*Abre un bloque `try/except` para capturar cualquier error que MySQL pueda lanzar.*

```python
15:         conexion = mysql.connector.connect(**DB_CONFIG)
```
*Construye la conexión usando los valores del diccionario (`**` “desempaqueta” los pares clave‑valor como argumentos de la función).*

```python
18:         if conexion.is_connected():
```
*Comprueba que la conexión esté realmente establecida; `is_connected()` devuelve `True` sólo si la conexión está activa.*

```python
19:             print("\n✅ ¡ÉXITO! Conexión establecida correctamente.")
```
*Mensaje de éxito.*

```python
22:             info_servidor = conexion.get_server_info()
23:             print(f"📦 Versión del servidor MySQL: {info_servidor}")
```
*Obtiene la versión del servidor MySQL y la muestra.*

```python
25:             conexion.close()
26:             print("🔒 Conexión cerrada correctamente.")
```
*Cierra la conexión (buena práctica) e informa al usuario.*

```python
29:     except mysql.connector.Error as err:
```
*Este `except` captura sólo los errores específicos de MySQL.*

```python
31:         print(f"\n❌ ERROR DE CONEXIÓN:")
32:         if err.errno == 1045:
33:             print("Problema: Usuario o contraseña incorrectos.")
34:         elif err.errno == 2003:
35:             print("Problema: No se puede conectar al servidor. ¿Está encendido MySQL?")
36:         elif err.errno == 1049:
37:             print(f"Problema: La base de datos '{DB_CONFIG['database']}' no existe.")
38:         else:
39:             print(f"Detalle técnico: {err}")
```
*Maneja diferentes códigos de error y muestra mensajes claros para los casos más comunes (credenciales erróneas, servidor fuera de línea, base de datos inexistente).*

```python
41: if __name__ == "__main__":
42:     probar_conexion()
```
*Si el archivo se ejecuta directamente (`python prueba_conexion.py`), llama a la función anterior.*

---

## 2. `mysql_mcp_server.py`

```python
1: from mcp.server.fastmcp import FastMCP
2: import mysql.connector
```
*Importa la clase `FastMCP` (servidor MCP ligero) y el driver de MySQL.*

```python
4: # 1. Inicializamos el servidor MCP
5: mcp = FastMCP("Servidor_MySQL_Local")
```
*Crea una instancia del servidor MCP con el nombre “Servidor_MySQL_Local”. Este objeto gestionará la comunicación con los clientes que quieran usar las herramientas que definiremos a continuación.*

```python
7: # 2. Configura tus credenciales de MySQL (las mismas de Workbench)
8: DB_CONFIG = {
9:     "host": "127.0.0.1",
10:    "user": "root",           # Cambia por tu usuario
11:    "password": "********$", # Cambia por tu contraseña
12:    "database": "Prueba" # Cambia por tu BD
13: }
```
*Igual que en `prueba_conexion.py`, define los datos de acceso a la base.*

```python
15: def obtener_conexion():
16:     return mysql.connector.connect(**DB_CONFIG)
```
*Función de conveniencia que devuelve una nueva conexión MySQL preparada con la configuración anterior.*

```python
18: # 3. Creamos una herramienta (Tool) que el modelo local podrá ejecutar
19: # --- HERRAMIENTA 1: SOLO LECTURA ---
20: @mcp.tool()
21: def leer_datos_mysql(query: str) -> str:
```
*Decorador `@mcp.tool()` registra la función como una “herramienta” disponible para el modelo. `leer_datos_mysql` recibirá una cadena SQL y devolverá una cadena con el resultado.*

```python
23:     """
24:     Usa esta herramienta SOLO para leer datos o ver la estructura.
25:     Ejecuta consultas SELECT, SHOW TABLES, DESCRIBE, etc.
26:     NO uses esta herramienta para insertar o crear tablas.
27:     """
```
*Docstring que describe la intención de la herramienta y sirve como ayuda para el modelo.*

```python
28:     try:
29:         if not query.strip().upper().startswith(("SELECT", "SHOW", "DESCRIBE", "EXPLAIN")):
30:             return "Error: Esta herramienta es solo para lectura. Usa 'modificar_base_datos' para otras acciones."
```
*Valida que la consulta empiece por una palabra de lectura; si no, devuelve un mensaje de error.*

```python
32:         conn = obtener_conexion()
33:         cursor = conn.cursor(dictionary=True)
34:         cursor.execute(query)
35:         resultados = cursor.fetchall()
36:         conn.close()
```
*Abre la conexión, crea un cursor que devuelve filas como diccionarios (`dictionary=True`), ejecuta la consulta y captura todas las filas (`fetchall`). Luego cierra la conexión.*

```python
38:         return str(resultados) if resultados else "La consulta se ejecutó sin errores, pero está vacía."
```
*Convierte la lista de diccionarios a cadena para enviarla como respuesta. Si no hay filas, informa que la tabla está vacía.*

```python
40:     except Exception as e:
41:         return f"Error en lectura: {e}"
```
*Cualquier excepción (p.ej. sintaxis SQL incorrecta) se captura y se devuelve como texto.*

```python
43: # --- HERRAMIENTA 2: ESCRITURA Y MODIFICACIÓN ---
44: @mcp.tool()
45: def modificar_base_datos(query: str) -> str:
```
*Segunda herramienta, esta vez para operaciones que modifican la BD (INSERT, UPDATE, CREATE, DELETE, ALTER, DROP).*

```python
47:     """
48:     Usa esta herramienta para MODIFICAR la base de datos.
49:     Permite comandos como CREATE TABLE, INSERT, UPDATE, DELETE, ALTER o DROP.
50:     """
```
*Docstring que explica su finalidad.*

```python
51:     try:
52:         # Prevenir que use esta herramienta solo para leer (buenas prácticas para el modelo)
53:         if query.strip().upper().startswith(("SELECT", "SHOW", "DESCRIBE")):
54:             return "Aviso: Estás intentando leer datos. Por favor, usa la herramienta 'leer_datos_mysql' para esto."
```
*Verifica que la consulta NO sea de solo lectura; si lo es, indica al modelo que use la herramienta adecuada.*

```python
56:         conn = obtener_conexion()
57:         cursor = conn.cursor()
58:         cursor.execute(query)
59:         
60:         # ¡MUY IMPORTANTE! Confirmamos los cambios en la base de datos
61:         conn.commit()
```
*Ejecuta la consulta, luego llama a `commit()` para que los cambios se persistan.*

```python
63:         filas_afectadas = cursor.rowcount
64:         conn.close()
65:         
66:         return f"Éxito. La operación se realizó correctamente. Filas afectadas/creadas: {filas_afectadas}"
```
*Obtiene cuántas filas fueron afectadas por la operación (`rowcount`), cierra la conexión y devuelve un mensaje con ese número.*

```python
68:     except mysql.connector.Error as err:
69:         return f"Error de MySQL al modificar: {err}"
70:     except Exception as e:
71:         return f"Error inesperado al modificar: {e}"
```
*Captura errores específicos de MySQL por separado de cualquier otro tipo de excepción, devolviendo un mensaje descriptivo.*

```python
73: if __name__ == "__main__":
74:     # Inicia el servidor MCP usando STDIO (estándar para clientes MCP)
75:     mcp.run()
```
*Cuando el script se ejecuta directamente (`python mysql_mcp_server.py`) lanza el bucle del servidor MCP. La comunicación con los clientes se realiza vía STDIO (entrada/salida estándar), lo que permite que otro proceso (el cliente) se conecte mediante tuberías.*

---

## 3. `cliente_mcp.py`

```python
1: import asyncio
2: from ollama import AsyncClient
3: from mcp import ClientSession, StdioServerParameters
4: from mcp.client.stdio import stdio_client
```
*Importa los módulos necesarios: `asyncio` para programación asíncrona, `AsyncClient` de Ollama (cliente para el modelo local), y los componentes de `mcp` que permiten crear una sesión cliente‑servidor mediante STDIO.*

```python
7: MODELO = 'qwen3.5:9b' 
```
*Define el modelo de Ollama que se usará. Cambiar esta cadena permite probar otros modelos instalados.*

```python
9: async def iniciar_cliente():
```
*Función asíncrona que contiene todo el flujo del cliente.*

```python
11:     # 1. Configurar cómo vamos a ejecutar el servidor MCP
12:     # Usamos 'python' para ejecutar el script del servidor que creamos antes
13:     parametros_servidor = StdioServerParameters(
14:         command="python", 
15:         args=["mysql_mcp_server.py"] # Asegúrate de que el nombre coincida
16:     )
```
*Crea un objeto `StdioServerParameters` que indica que el proceso del servidor será lanzado con `python mysql_mcp_server.py`. Este objeto será usado por `stdio_client` para abrir una tubería de entrada/salida entre cliente y servidor.*

```python
18:     # 2. Iniciar la conexión stdio con el servidor MCP
19:     async with stdio_client(parametros_servidor) as (lectura, escritura):
20:         async with ClientSession(lectura, escritura) as sesion:
21:             await sesion.initialize()
```
*Abre la conexión STDIO y crea una `ClientSession` que envuelve los streams de lectura y escritura. `initialize()` intercambia los metadatos iniciales y deja lista la sesión para enviar/recibir mensajes y llamar a herramientas.*

```python
23:             # 3. Obtener las herramientas del servidor MCP
24:             mcp_tools = await sesion.list_tools()
```
*Envía una petición al servidor para obtener la lista de herramientas (`leer_datos_mysql` y `modificar_base_datos`).*

```python
26:             # Convertir el formato de herramientas de MCP al formato que entiende Ollama
27:             ollama_tools = []
28:             for tool in mcp_tools.tools:
29:                 ollama_tools.append({
30:                     "type": "function",
31:                     "function": {
32:                         "name": tool.name,
33:                         "description": tool.description,
34:                         "parameters": tool.inputSchema
35:                     }
36:                 })
```
*Transforma cada herramienta recibida a la estructura que Ollama espera en su campo `tools` (tipo `function`). Esto permite que el modelo “vea” las funciones disponibles y pueda decidir llamarlas.*

```python
38:             print(f"¡Conectado a la base de datos! Herramientas cargadas: {[t.name for t in mcp_tools.tools]}")
39:             print("Escribe 'salir' para terminar el chat.\n")
```
*Mensaje informativo al usuario.*

```python
41:             # 4. Inicializar cliente de Ollama y el historial de mensajes
42:             cliente_ollama = AsyncClient(host='http://localhost:11434')
43:             mensajes = []
```
*Crea el cliente que hablará con el servidor local de Ollama (por defecto en `localhost:11434`). `mensajes` mantiene el historial de la conversación, necesario para que Ollama tenga contexto.*

```python
45:             # 5. Iniciar el bucle de chat
46:             while True:
47:                 texto_usuario = input("🗿 Tú: ")
48:                 if texto_usuario.lower() in ['salir', 'exit', 'quit']:
49:                     break
```
*Bucle interactivo: lee la entrada del usuario y permite salir escribiendo *salir*, *exit* o *quit*.*

```python
51:                 mensajes.append({"role": "user", "content": texto_usuario})
```
*Agrega el mensaje del usuario al historial.*

```python
53:                 # Enviar mensaje a Ollama junto con las herramientas disponibles
54:                 respuesta = await cliente_ollama.chat(
55:                     model=MODELO,
56:                     messages=mensajes,
57:                     tools=ollama_tools
58:                 )
```
*Envía la conversación completa (incluyendo historial) y la lista de herramientas al modelo. Ollama decide si responde directamente o si necesita ejecutar alguna herramienta.*

```python
60:                 # Guardar la respuesta inicial en el historial
61:                 mensaje_ia = respuesta['message']
62:                 mensajes.append(mensaje_ia)
```
*Guarda la respuesta de Ollama (puede incluir `tool_calls`) en el historial.*

```python
64:                 # 6. Comprobar si Ollama decidió usar una herramienta (Tool Call)
65:                 if mensaje_ia.get('tool_calls'):
66:                     for tool_call in mensaje_ia['tool_calls']:
67:                         nombre_herramienta = tool_call['function']['name']
68:                         argumentos = tool_call['function']['arguments']
```
*Si la respuesta contiene `tool_calls`, iteramos sobre cada llamada. Cada llamada incluye el nombre de la herramienta y los argumentos (p.ej. una cadena SQL).*

```python
70:                         print(f"\n[⚙️ El modelo está ejecutando: {nombre_herramienta}]")
71:                         print(f"[⚙️ Argumentos: {argumentos}]")
```
*Feedback visual para el usuario.*

```python
73:                         # Ejecutar la herramienta a través de nuestro servidor MCP
74:                         resultado_mcp = await sesion.call_tool(nombre_herramienta, argumentos)
```
*Invoca la herramienta en el servidor MCP. `call_tool` envía la petición con el nombre y los argumentos y recibe la respuesta.*

```python
76:                         # Extraer el texto del resultado de la base de datos
77:                         texto_resultado = resultado_mcp.content[0].text
```
*`resultado_mcp` es un objeto `Message`. Su primer elemento (`content[0]`) contiene el texto devuelto por la herramienta (por ejemplo, el JSON de resultados de una consulta).*

```python
79:                         # Enviar el resultado de la herramienta de vuelta a Ollama
80:                         mensajes.append({
81:                             "role": "tool",
82:                             "name": nombre_herramienta,
83:                             "content": texto_resultado
84:                         })
```
*Agrega al historial un mensaje con rol `tool` que contiene la salida de la herramienta. Ollama lo usará como contexto para generar la respuesta final.*

```python
86:                     # 7. Hacer una SEGUNDA llamada a Ollama para que lea los datos y responda
87:                     respuesta_final = await cliente_ollama.chat(
88:                         model=MODELO,
89:                         messages=mensajes
90:                     )
91:                     mensajes.append(respuesta_final['message'])
92:                     print(f"\nIA: {respuesta_final['message']['content']}\n")
```
*Con el resultado de la herramienta ya incluido en el historial, se vuelve a llamar a Ollama (sin pasar la lista de `tools` porque ya no necesita una nueva herramienta). La respuesta final del modelo se muestra al usuario.*

```python
94:                 # Si no usó herramientas, simplemente imprimimos lo que dijo
95:                 else:
96:                     print(f"\nIA: {mensaje_ia['content']}\n")
```
*Caso en que el modelo responde directamente sin necesidad de ejecutar ninguna herramienta.*

```python
98: if __name__ == "__main__":
99:     # Como MCP y Ollama Async usan operaciones asíncronas, usamos asyncio para correr el script
100:    asyncio.run(iniciar_cliente())
```
*Punto de entrada del script: ejecuta la función asíncrona `iniciar_cliente` usando el bucle de eventos de `asyncio`.*

---

## 4. `main.py`

```python
1: def main():
2:     print("Hello from mcp-sql!")
3: 
4: 
5: if __name__ == "__main__":
6:     main()
```
*Archivo de ejemplo muy simple que solo muestra un mensaje por consola. No tiene relación con la lógica del servidor/cliente; sirve como “placeholder” o punto de partida para pruebas rápidas.*

---

# Resumen general del flujo

1. **`prueba_conexion.py`** verifica que la base de datos MySQL sea accesible con la configuración proveída.  
2. **`mysql_mcp_server.py`** levanta un *servidor MCP* que expone dos funciones (`leer_datos_mysql` y `modificar_base_datos`) como “herramientas” que pueden ser invocadas remotamente.  
3. **`cliente_mcp.py`**:
   - Inicia el servidor anterior vía STDIO.  
   - Conecta con Ollama (modelo local).  
   - Envía al modelo el historial de conversación y la lista de herramientas.  
   - Cuando Ollama decide que necesita ejecutar una herramienta, el cliente llama al servidor MCP, obtiene el resultado y vuelve a enviar al modelo para que genere la respuesta final al usuario.  
4. **`main.py`** es un simple “hello world”; no interviene en el flujo real.  

Este esquema permite que cualquier usuario converse en lenguaje natural con una IA que, bajo demanda, ejecuta consultas SQL contra su base de datos sin que el usuario tenga que recordar la sintaxis exacta. La separación cliente‑servidor (STDIO) hace que el modelo sea totalmente agnóstico al entorno de base de datos; solo necesita conocer la descripción de las funciones.

---

**Fin del tutorial.**