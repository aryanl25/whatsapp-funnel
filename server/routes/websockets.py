from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from server.services.websocket_manager import manager
from server.dependencies import get_ws_auth_context, get_db
from sqlalchemy.orm import Session
from server.schemas import AuthContext
from typing import Optional, Dict, Any
import time
from server.services.websocket_events import WSEvents

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    db: Session = Depends(get_db)
):
    auth: Optional[AuthContext] = await get_ws_auth_context(token, db)
    if auth is None:
        await websocket.accept()
        await websocket.send_json({"error": "Unauthorized"})
        await websocket.close(code=1008)
        return

    await manager.connect(websocket, auth.organization_id)

    try:
        # Let frontend know connection is ready
        await websocket.send_json({
            "event": WSEvents.SERVER_HELLO,
            "payload": {"organization_id": str(auth.organization_id)},
        })

        while True:
            data: Dict[str, Any] = await websocket.receive_json()
            event = data.get("event")

            if event == WSEvents.CLIENT_HEARTBEAT:
                await websocket.send_json({
                    "event": WSEvents.ACK,
                    "payload": {"ts": int(time.time())},
                })
                continue

            # unknown client event
            await websocket.send_json({
                "event": WSEvents.ERROR,
                "payload": {"message": f"Unknown event: {event}"},
            })

    except WebSocketDisconnect:
        manager.disconnect(websocket, auth.organization_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, auth.organization_id)