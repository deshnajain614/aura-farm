"""
AURA-Farm Main Application Entry Point
======================================
Launches the FastAPI server and background autonomous agricultural operating system.
"""
import uvicorn
import logging
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from aura_farm.config import config
from aura_farm.api.server import app

def main():
    print("=" * 70)
    print("  [AURA-Farm] Autonomous Unified Robotic Agriculture Farm OS")
    print("  Zero-Routine-Human-Intervention Closed-Loop Architecture")
    print("=" * 70)
    print(f"  Server running on http://{config.host}:{config.port}")
    print(f"  Web Dashboard:   http://localhost:{config.port}")
    print(f"  REST API Docs:   http://localhost:{config.port}/docs")
    print("=" * 70)

    uvicorn.run(
        "aura_farm.api.server:app",
        host=config.host,
        port=config.port,
        reload=False,
        log_level="info"
    )

if __name__ == "__main__":
    main()
