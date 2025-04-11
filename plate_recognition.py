import cv2
import numpy as np
import torch
import asyncio
import logging
import json
from datetime import datetime
from hikvisionapi import Client
from dotenv import load_dotenv
import os
import websockets

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PlateRecognition:
    def __init__(self):
        load_dotenv()
        
        # Configurações do DVR
        self.dvr_ip = os.getenv("DVR_IP")
        self.dvr_port = os.getenv("DVR_PORT")
        self.dvr_username = os.getenv("DVR_USERNAME")
        self.dvr_password = os.getenv("DVR_PASSWORD")
        self.camera_channels = [int(ch) for ch in os.getenv("CAMERA_CHANNELS").split(",")]
        
        # Configurações do WebSocket
        self.ws_host = os.getenv("WEBSOCKET_HOST")
        self.ws_port = os.getenv("WEBSOCKET_PORT")
        
        # Carregando modelos
        self.load_models()
        
        # Conexão com DVR
        self.dvr = Client(
            host=self.dvr_ip,
            username=self.dvr_username,
            password=self.dvr_password,
            port=self.dvr_port
        )

    def load_models(self):
        # Carregando o modelo YOLO treinado para placas
        self.plate_model = torch.hub.load('ultralytics/yolov5', 'custom', 
                                        path='modelo_placas.pt')
        
        # Carregando o Haar Cascade
        self.plate_cascade = cv2.CascadeClassifier('haarcascade_russian_plate_number.xml')
        
        logger.info("Modelos carregados com sucesso")

    async def send_plate_data(self, plate_data):
        uri = f"ws://{self.ws_host}:{self.ws_port}"
        async with websockets.connect(uri) as websocket:
            await websocket.send(json.dumps(plate_data))

    def process_frame(self, frame, camera_id):
        # Convertendo para escala de cinza para o Haar Cascade
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detectando região da placa com Haar Cascade
        plates = self.plate_cascade.detectMultiScale(gray, 1.1, 4)
        
        for (x, y, w, h) in plates:
            # Recortando a região da placa
            plate_region = frame[y:y+h, x:x+w]
            
            # Usando o modelo YOLO para reconhecer a placa
            results = self.plate_model(plate_region)
            
            # Processando resultados
            if len(results.xyxy[0]) > 0:
                for detection in results.xyxy[0]:
                    confidence = detection[4].item()
                    if confidence > 0.5:  # Threshold de confiança
                        plate_text = results.names[int(detection[5])]
                        
                        plate_data = {
                            "plate": plate_text,
                            "camera_id": camera_id,
                            "confidence": confidence,
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        # Enviando dados via WebSocket
                        asyncio.create_task(self.send_plate_data(plate_data))
                        
                        logger.info(f"Placa detectada: {plate_text} (Confiança: {confidence:.2f})")

    async def process_cameras(self):
        while True:
            for channel in self.camera_channels:
                try:
                    # Capturando frame do DVR
                    frame = self.dvr.Streaming.getStream(channel=channel)
                    
                    # Convertendo frame para formato numpy
                    np_frame = np.array(frame)
                    
                    # Processando o frame
                    self.process_frame(np_frame, channel)
                    
                except Exception as e:
                    logger.error(f"Erro ao processar câmera {channel}: {str(e)}")
                
            await asyncio.sleep(0.1)  # Pequeno delay para não sobrecarregar

async def main():
    plate_recognition = PlateRecognition()
    await plate_recognition.process_cameras()

if __name__ == "__main__":
    asyncio.run(main()) 