# websocket_manager.py
from fastapi import WebSocket
from typing import Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}  # user_id → socket

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active_connections.pop(user_id, None)

    async def notify_user(self, user_id: str, message: dict):
        ws = self.active_connections.get(str(user_id))
        if ws:
            await ws.send_json(message)

manager = ConnectionManager()