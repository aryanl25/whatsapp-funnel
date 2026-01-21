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

    # Connect with both user_id and org_id
    await manager.connect(websocket, auth.user_id, auth.organization_id)

    try:
        # Let frontend know connection is ready
        await websocket.send_json({
            "event": WSEvents.SERVER_HELLO,
            "payload": {"organization_id": str(auth.organization_id), "user_id": str(auth.user_id)},
        })

        while True:
            data: Dict[str, Any] = await websocket.receive_json()
            # Delegate all processing to manager
            await manager.handle_incoming(auth.user_id, data)

    except WebSocketDisconnect:
        manager.disconnect(websocket, auth.user_id, auth.organization_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket, auth.user_id, auth.organization_id)