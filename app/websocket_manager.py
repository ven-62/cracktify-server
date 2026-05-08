# websocket_manager.py
from fastapi import WebSocket, HTTPException
from typing import Dict

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}  # user_id → socket

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            self.active_connections.pop(user_id, None)

    async def notify_user(self, user_id: str, message: dict):
        ws = self.active_connections.get(str(user_id))
        
        if not ws:
            raise HTTPException(status_code=404, detail=f"User {user_id} not connected")
        
        await ws.send_json(message)
        self.disconnect(user_id)  # Clean up if send fails


manager = ConnectionManager()