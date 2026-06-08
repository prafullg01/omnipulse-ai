"""WebSocket Connection Manager for real-time event broadcasting."""
import json
from datetime import datetime
from typing import Dict, List, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time event streaming."""
    
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}  # room -> connections
        self.all_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket, room: str = "global"):
        await websocket.accept()
        self.all_connections.append(websocket)
        if room not in self.active_connections:
            self.active_connections[room] = []
        self.active_connections[room].append(websocket)
    
    def disconnect(self, websocket: WebSocket, room: str = "global"):
        if websocket in self.all_connections:
            self.all_connections.remove(websocket)
        if room in self.active_connections and websocket in self.active_connections[room]:
            self.active_connections[room].remove(websocket)
    
    async def broadcast(self, message: dict, room: str = "global"):
        """Broadcast message to all connections in a room."""
        connections = self.active_connections.get(room, []) + self.active_connections.get("global", [])
        seen = set()
        for conn in connections:
            if id(conn) not in seen:
                seen.add(id(conn))
                try:
                    await conn.send_json(message)
                except Exception:
                    pass
    
    async def broadcast_event(self, event_type: str, data: dict):
        """Broadcast a customer event to all admin connections."""
        message = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self.broadcast(message, "admin")
        await self.broadcast(message, "global")
    
    @property
    def connection_count(self) -> int:
        return len(self.all_connections)


# Singleton manager
manager = ConnectionManager()


@router.websocket("/ws/{room}")
async def websocket_endpoint(websocket: WebSocket, room: str = "global"):
    await manager.connect(websocket, room)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo or process incoming messages
            try:
                msg = json.loads(data)
                await manager.broadcast(msg, room)
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        manager.disconnect(websocket, room)
