"""WebSocket utilities for EdgeFleet backend."""

import asyncio
import json
import logging
from typing import Callable, Dict, Set, Optional
from fastapi import WebSocket

logger = logging.getLogger("edgefleet.websocket")


class FleetWebSocketManager:
    """Manages WebSocket connections between backend and dashboard clients."""

    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self._subscriptions: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, client_id: str = "default"):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = set()
        self.active_connections[client_id].add(websocket)
        logger.info(f"Client connected: {client_id}")

    def disconnect(self, websocket: WebSocket, client_id: str = "default"):
        if client_id in self.active_connections:
            self.active_connections[client_id].discard(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
        logger.info(f"Client disconnected: {client_id}")

    async def broadcast(self, data: dict, channel: str = "fleet_state"):
        """Send data to all clients subscribed to a channel."""
        message = json.dumps(data)
        disconnected = []

        for client_id, connections in self.active_connections.items():
            for websocket in connections:
                try:
                    await websocket.send_text(message)
                except Exception:
                    disconnected.append((websocket, client_id))

        for ws, cid in disconnected:
            self.disconnect(ws, cid)

    async def send_to(self, client_id: str, data: dict):
        """Send data to a specific client."""
        if client_id in self.active_connections:
            message = json.dumps(data)
            for websocket in self.active_connections[client_id]:
                try:
                    await websocket.send_text(message)
                except Exception:
                    self.disconnect(websocket, client_id)

    @property
    def client_count(self) -> int:
        return sum(len(conns) for conns in self.active_connections.values())
