import asyncio
import websockets
import json
import random
from datetime import datetime
import logging
from dotenv import load_dotenv
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Lista de placas de exemplo para simulação
PLACAS_EXEMPLO = [
    "ABC1234",
    "XYZ5678",
    "DEF9012",
    "GHI3456",
    "JKL7890"
]

async def simulate_plate_detection():
    load_dotenv()
    
    host = os.getenv("WEBSOCKET_HOST", "localhost")
    port = int(os.getenv("WEBSOCKET_PORT", 8765))
    
    uri = f"ws://{host}:{port}"
    logger.info(f"Conectando ao servidor WebSocket em {uri}")
    
    while True:
        try:
            async with websockets.connect(uri) as websocket:
                logger.info("Conectado ao servidor WebSocket")
                
                while True:
                    # Gerando dados simulados
                    plate_data = {
                        "timestamp": datetime.now().isoformat(),
                        "plate": random.choice(PLACAS_EXEMPLO),
                        "camera_id": random.randint(1, 3),
                        "confidence": round(random.uniform(0.75, 0.99), 2)
                    }
                    
                    # Convertendo para JSON
                    message = json.dumps(plate_data)
                    
                    # Enviando dados
                    await websocket.send(message)
                    logger.info(f"Placa simulada enviada: {plate_data['plate']} " 
                              f"(Câmera: {plate_data['camera_id']}, "
                              f"Confiança: {plate_data['confidence']})")
                    
                    # Aguardando entre 2 a 5 segundos antes do próximo envio
                    await asyncio.sleep(random.uniform(2, 5))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("Conexão com WebSocket perdida. Tentando reconectar em 3 segundos...")
            await asyncio.sleep(3)
        except Exception as e:
            logger.error(f"Erro: {str(e)}")
            logger.error(f"Tipo do erro: {type(e)}")
            await asyncio.sleep(3)

if __name__ == "__main__":
    try:
        logger.info("Iniciando simulação de detecção de placas...")
        asyncio.run(simulate_plate_detection())
    except KeyboardInterrupt:
        logger.info("Simulador encerrado pelo usuário")
    except Exception as e:
        logger.error(f"Erro fatal no simulador: {e}") 