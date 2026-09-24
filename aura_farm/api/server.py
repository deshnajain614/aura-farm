"""
AURA-Farm FastAPI Server & WebSocket Real-Time Streamer
======================================================
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
import os
import logging
from aura_farm.api.routes import router
from aura_farm.orchestrator import orchestrator
from aura_farm.config import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("aura_farm.server")

# Active WebSocket clients
connected_clients = set()

async def background_orchestrator_loop():
    """Background task that runs the autonomous loop and broadcasts telemetry."""
    logger.info("Autonomous farm background loop started.")
    while True:
        try:
            if not orchestrator.state_machine.auto_advance_enabled:
                await asyncio.sleep(1.0)
                continue

            # Execute farm tick
            snapshot = orchestrator.tick()

            # Broadcast to all connected WebSocket clients
            if connected_clients:
                payload = json.dumps(snapshot)
                disconnected = set()
                for client in connected_clients:
                    try:
                        await client.send_text(payload)
                    except Exception:
                        disconnected.add(client)
                for client in disconnected:
                    connected_clients.remove(client)

            await asyncio.sleep(config.tick_rate_seconds)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in background loop: {e}")
            await asyncio.sleep(1.0)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: spawn background loop
    loop_task = asyncio.create_task(background_orchestrator_loop())
    yield
    # Shutdown
    loop_task.cancel()

app = FastAPI(
    title="AURA-Farm OS",
    description="Autonomous Unified Robotic Agriculture Farm Operating System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.websocket("/ws/telemetry")
async def websocket_telemetry(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        # Immediately send current state upon connection
        await websocket.send_text(json.dumps(orchestrator.get_telemetry_snapshot()))
        while True:
            # Handle incoming messages from UI if any
            data = await websocket.receive_text()
            cmd = json.loads(data)
            if cmd.get("action") == "TICK":
                snapshot = orchestrator.tick()
                await websocket.send_text(json.dumps(snapshot))
    except WebSocketDisconnect:
        connected_clients.remove(websocket)
    except Exception:
        if websocket in connected_clients:
            connected_clients.remove(websocket)

# Mount web dashboard
web_dir = os.path.join(os.path.dirname(__file__), "..", "web")
if os.path.exists(web_dir):
    app.mount("/", StaticFiles(directory=web_dir, html=True), name="web")
