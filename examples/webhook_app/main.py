import logging
import json
from typing import Any, Dict, List
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Z-API Webhook Viewer")

# Mount static files
app.mount("/static", StaticFiles(directory="examples/webhook_app/static"), name="static")

# Templates
templates = Jinja2Templates(directory="examples/webhook_app/templates")

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to websocket: {e}")

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- Webhook Endpoints ---

async def process_webhook(event_type: str, payload: Dict[str, Any]):
    """Process and broadcast webhook event."""
    logger.info(f"Received {event_type}: {payload}")
    
    event_data = {
        "type": event_type,
        "payload": payload,
        "timestamp": payload.get("momment") or payload.get("moment")  # Handle API typo/variation
    }
    
    await manager.broadcast(event_data)
    return {"status": "received"}

@app.post("/whatsapp/receive")
async def receive_message(request: Request):
    payload = await request.json()
    return await process_webhook("RECEIVED_MESSAGE", payload)

@app.post("/whatsapp/status")
async def receive_status(request: Request):
    payload = await request.json()
    return await process_webhook("MESSAGE_STATUS", payload)

@app.post("/whatsapp/connect")
async def receive_connect(request: Request):
    payload = await request.json()
    return await process_webhook("INSTANCE_CONNECTED", payload)

@app.post("/whatsapp/disconnect")
async def receive_disconnect(request: Request):
    payload = await request.json()
    return await process_webhook("INSTANCE_DISCONNECTED", payload)

@app.post("/whatsapp/presence")
async def receive_presence(request: Request):
    payload = await request.json()
    return await process_webhook("CHAT_PRESENCE", payload)

@app.post("/whatsapp/send")
async def receive_send(request: Request):
    payload = await request.json()
    return await process_webhook("SENT_MESSAGE", payload)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("examples.webhook_app.main:app", host="0.0.0.0", port=8000, reload=True)
