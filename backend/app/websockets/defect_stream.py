"""
Defect Stream WebSocket Handler
================================
Provides a real-time WebSocket endpoint that pushes live defect detection
events to connected dashboard clients.

Protocol:
  Client connects → WS /ws/defects/{line_id}
  Server pushes JSON: { type: 'defect', data: DefectEventPayload }
  Server pushes JSON: { type: 'grade_update', data: GradePayload }
  Server pushes JSON: { type: 'heartbeat', ts: ISO8601 }

TODO:
  - Implement WebSocket manager with per-line broadcast rooms
  - Wire the AI inference module to push events into this manager
  - Add JWT auth validation for WS handshake
"""

from fastapi import WebSocket


class ConnectionManager:
    """Manages active WebSocket connections, grouped by production line."""

    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, line_id: int):
        await websocket.accept()
        self.active_connections.setdefault(line_id, []).append(websocket)

    def disconnect(self, websocket: WebSocket, line_id: int):
        if line_id in self.active_connections:
            self.active_connections[line_id].remove(websocket)

    async def broadcast(self, message: dict, line_id: int):
        for ws in self.active_connections.get(line_id, []):
            await ws.send_json(message)


manager = ConnectionManager()
