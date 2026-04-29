from fastapi import APIRouter

from app.api import files, conversion, metadata, ws

router = APIRouter(prefix="/api/v1")

router.include_router(files.router, prefix="/files", tags=["files"])
router.include_router(conversion.router, prefix="/conversion", tags=["conversion"])
router.include_router(metadata.router, prefix="/metadata", tags=["metadata"])
router.include_router(ws.router, prefix="/ws", tags=["websocket"])
