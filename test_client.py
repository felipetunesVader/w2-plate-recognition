import asyncio
import websockets
import json
import logging
from dotenv import load_dotenv
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def receive_plates():
    load_dotenv()
    
    host = os.getenv("WEBSOCKET_HOST", "localhost")
    port = int(os.getenv("WEBSOCKET_PORT", 8765))
    
    uri = f"ws://{host}:{port}"
    
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                logger.info("Conectado ao servidor WebSocket. Aguardando placas...")
                
                while True:
                    message = await websocket.recv()
                    logger.debug(f"Mensagem recebida: {message}")
                    data = json.loads(message)
                    
                    logger.info("\n=== Nova Placa Detectada ===")
                    logger.info(f"Placa: {data['plate']}")
                    logger.info(f"Câmera: {data['camera_id']}")
                    logger.info(f"Confiança: {data['confidence']:.2f}")
                    logger.info(f"Timestamp: {data['timestamp']}")
                    logger.info("=========================")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Conexão perdida. Tentando reconectar...")
            await asyncio.sleep(3)
        except Exception as e:
            logger.error(f"Erro: {str(e)}")
            logger.error(f"Tipo do erro: {type(e)}")
            await asyncio.sleep(3)

if __name__ == "__main__":
    try:
        asyncio.run(receive_plates())
    except KeyboardInterrupt:
        logger.info("Aplicação encerrada pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal: {str(e)}") 