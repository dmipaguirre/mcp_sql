import asyncio
from ollama import AsyncClient
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Cambia esto por el modelo que tengas descargado en Ollama
MODELO = "gemma4:e4b"


async def iniciar_cliente():
    # 1. Configurar cómo vamos a ejecutar el servidor MCP
    # Usamos 'python' para ejecutar el script del servidor que creamos antes
    parametros_servidor = StdioServerParameters(
        command="python", args=["mysql_mcp_server.py"]
    )

    # 2. Iniciar la conexión stdio con el servidor MCP
    async with stdio_client(parametros_servidor) as (lectura, escritura):
        async with ClientSession(lectura, escritura) as sesion:
            await sesion.initialize()

            # 3. Obtener las herramientas del servidor MCP
            mcp_tools = await sesion.list_tools()

            # Convertir el formato de herramientas de MCP al formato que entiende Ollama
            ollama_tools = []
            for tool in mcp_tools.tools:
                ollama_tools.append(
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.inputSchema,
                        },
                    }
                )

            print(
                f"¡Conectado a la base de datos! Herramientas cargadas: {[t.name for t in mcp_tools.tools]}"
            )
            print("Escribe 'salir' para terminar el chat.\n")

            # Inicializar cliente de Ollama y el historial de mensajes
            cliente_ollama = AsyncClient(host="http://localhost:11434")
            mensajes = []

            # 4. Iniciar el bucle de chat
            while True:
                texto_usuario = input("🗿 Tú: ")
                if texto_usuario.lower() in ["salir", "exit", "quit",]:
                    break

                mensajes.append({"role": "user", "content": texto_usuario})

                # Enviar mensaje a Ollama junto con las herramientas disponibles
                respuesta = await cliente_ollama.chat(
                    model=MODELO, messages=mensajes, tools=ollama_tools
                )

                # Guardar la respuesta inicial en el historial
                mensaje_ia = respuesta["message"]
                mensajes.append(mensaje_ia)

                # 5. Comprobar si Ollama decidió usar una herramienta (Tool Call)
                if mensaje_ia.get("tool_calls"):
                    for tool_call in mensaje_ia["tool_calls"]:
                        nombre_herramienta = tool_call["function"]["name"]
                        argumentos = tool_call["function"]["arguments"]

                        print(f"\n[⚙️ El modelo está ejecutando: {nombre_herramienta}]")
                        print(f"[⚙️ Argumentos: {argumentos}]")

                        # Ejecutar la herramienta a través de nuestro servidor MCP
                        resultado_mcp = await sesion.call_tool(
                            nombre_herramienta, argumentos
                        )

                        # Extraer el texto del resultado de la base de datos
                        texto_resultado = resultado_mcp.content[0].text

                        # Enviar el resultado de la herramienta de vuelta a Ollama
                        mensajes.append(
                            {
                                "role": "tool",
                                "name": nombre_herramienta,
                                "content": texto_resultado,
                            }
                        )

                    # 6. Hacer una SEGUNDA llamada a Ollama para que lea los datos y responda
                    respuesta_final = await cliente_ollama.chat(
                        model=MODELO, messages=mensajes
                    )
                    mensajes.append(respuesta_final["message"])
                    print(f"\nIA: {respuesta_final['message']['content']}\n")

                # Si no usó herramientas, simplemente imprimimos lo que dijo
                else:
                    print(f"\nIA: {mensaje_ia['content']}\n")


if __name__ == "__main__":
    # Como MCP y Ollama Async usan operaciones asíncronas, usamos asyncio para correr el script
    asyncio.run(iniciar_cliente())
