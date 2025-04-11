import asyncio
import websockets
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

connected_clients = set()

async def register(websocket):
    connected_clients.add(websocket)
    try:
        await websocket.wait_closed()
    finally:
        connected_clients.remove(websocket)

async def broadcast_plate(plate_data):
    if not connected_clients:
        logger.warning("Nenhum cliente conectado para receber os dados")
        return

    message = json.dumps({
        "timestamp": datetime.now().isoformat(),
        "plate": plate_data["plate"],
        "camera_id": plate_data["camera_id"],
        "confidence": plate_data["confidence"]
    })

    await asyncio.gather(
        *[client.send(message) for client in connected_clients]
    )

async def main():
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    
    host = os.getenv("WEBSOCKET_HOST", "localhost")
    port = int(os.getenv("WEBSOCKET_PORT", 8765))
    
    async with websockets.serve(register, host, port):
        logger.info(f"Servidor WebSocket iniciado em ws://{host}:{port}")
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main()) 