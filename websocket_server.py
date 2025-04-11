import asyncio
import websockets
import json
import logging
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Set para armazenar clientes conectados
connected_clients = set()

async def handle_client(websocket):
    # Adiciona o cliente ao set de conexões
    connected_clients.add(websocket)
    logger.info(f"Novo cliente conectado. Total de clientes: {len(connected_clients)}")
    
    try:
        async for message in websocket:
            try:
                # Log da mensagem recebida
                logger.debug(f"Mensagem recebida: {message}")
                
                # Tenta parsear a mensagem como JSON
                data = json.loads(message)
                
                # Envia a mensagem para todos os outros clientes
                for client in connected_clients:
                    if client != websocket:  # Não envia de volta para o remetente
                        try:
                            await client.send(message)
                            logger.debug(f"Mensagem encaminhada para cliente")
                        except Exception as e:
                            logger.error(f"Erro ao enviar mensagem para cliente: {e}")
                
            except json.JSONDecodeError:
                logger.error(f"Mensagem recebida não é um JSON válido: {message}")
            except Exception as e:
                logger.error(f"Erro ao processar mensagem: {e}")
    
    except websockets.exceptions.ConnectionClosed:
        logger.info("Cliente desconectou normalmente")
    except Exception as e:
        logger.error(f"Erro na conexão do cliente: {e}")
    finally:
        # Remove o cliente do set de conexões
        connected_clients.remove(websocket)
        logger.info(f"Cliente desconectado. Total de clientes: {len(connected_clients)}")

async def main():
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    host = os.getenv("WEBSOCKET_HOST", "localhost")
    port = int(os.getenv("WEBSOCKET_PORT", 8765))
    
    async with websockets.serve(handle_client, host, port):
        logger.info(f"Servidor WebSocket iniciado em ws://{host}:{port}")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Servidor encerrado pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal no servidor: {e}") 