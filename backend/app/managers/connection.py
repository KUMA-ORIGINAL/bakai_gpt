from fastapi import WebSocket
from typing import Dict


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_message_to_user(self, message: str, user_id: int):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)
