"""
LuminaLearn AI — Port Ownership Checks.
Module: backend/app/core/port_guard.py

On Windows two programs can listen on the same port, and the other one may receive every
request. Splunk owns 8000 on some machines, for example. Uvicorn then starts cleanly while the
frontend only ever reaches the other program. These checks turn that silent failure into a clear
message: `python -m app` refuses an occupied port up front, and a running server confirms that
its own port actually reaches it.
"""

import asyncio
import logging
import os
import socket
import sys
import uuid

import httpx

logger = logging.getLogger("uvicorn.error")

# Unique per process. The health endpoint echoes it, so a server can tell its own reply apart
# from another program answering on the same port.
INSTANCE_ID = uuid.uuid4().hex

UVICORN_DEFAULT_PORT = 8000


def port_in_use(port: int, host: str = "127.0.0.1") -> bool:
    """True when something already accepts connections on host:port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.settimeout(0.5)
        return probe.connect_ex((host, port)) == 0


def serving_port(argv: list[str] | None = None) -> int:
    """The port uvicorn was started with: --port N, --port=N, $UVICORN_PORT, else uvicorn's default."""
    args = sys.argv if argv is None else argv
    for index, arg in enumerate(args):
        if arg == "--port" and index + 1 < len(args) and args[index + 1].isdigit():
            return int(args[index + 1])
        if arg.startswith("--port=") and arg.split("=", 1)[1].isdigit():
            return int(arg.split("=", 1)[1])
    env_port = os.environ.get("UVICORN_PORT", "")
    return int(env_port) if env_port.isdigit() else UVICORN_DEFAULT_PORT


async def reaches_this_process(port: int) -> bool | None:
    """True when 127.0.0.1:port answers as this process, False when another program answers, None if unknown."""
    try:
        async with httpx.AsyncClient(timeout=3.0, follow_redirects=False) as client:
            response = await client.get(f"http://127.0.0.1:{port}/api/v1/health")
    except httpx.HTTPError:
        return None
    try:
        body = response.json()
    except ValueError:
        return False
    return isinstance(body, dict) and body.get("instance") == INSTANCE_ID


async def warn_if_port_shadowed(port: int, delay_seconds: float = 1.5) -> None:
    """Log a loud error when the port this server listens on is answered by another program."""
    await asyncio.sleep(delay_seconds)  # let uvicorn finish binding before probing
    if await reaches_this_process(port) is False:
        logger.error(
            "Port %s is answered by another program, so the frontend cannot reach this server. "
            "Stop this server and start it with `python -m app` (uses BACKEND_PORT from .env), "
            "or pass a free port such as --port 8001.",
            port,
        )
