# Sistema de Reconhecimento de Placas com DVR

Este sistema realiza o reconhecimento de placas de veículos através de câmeras conectadas a um DVR, utilizando modelos de IA para detecção e reconhecimento de placas brasileiras.

## Requisitos

- Python 3.8+
- DVR compatível com protocolo Hikvision (ou ajuste o código para seu DVR específico)
- Modelo YOLOv5 treinado para reconhecimento de placas (.pt)
- Haar Cascade para detecção de placas

## Configuração

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Configure as variáveis de ambiente:
- Copie o arquivo `.env.example` para `.env`
- Preencha as configurações do seu DVR e WebSocket

3. Coloque seus modelos na pasta raiz:
- `modelo_placas.pt` (seu modelo YOLOv5 treinado)
- `haarcascade_russian_plate_number.xml` (Haar Cascade)

## Executando o Sistema

1. Inicie o servidor WebSocket:
```bash
python websocket_server.py
```

2. Em outro terminal, inicie o reconhecimento de placas:
```bash
python plate_recognition.py
```

## Estrutura do Projeto

- `plate_recognition.py`: Código principal de reconhecimento de placas
- `websocket_server.py`: Servidor WebSocket para transmissão dos dados
- `requirements.txt`: Dependências do projeto
- `.env`: Configurações do sistema

## Formato dos Dados

O sistema envia os dados das placas reconhecidas via WebSocket no seguinte formato JSON:

```json
{
    "timestamp": "2024-01-01T12:00:00",
    "plate": "ABC1234",
    "camera_id": 1,
    "confidence": 0.95
}
``` 