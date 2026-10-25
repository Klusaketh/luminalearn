"""
Start the LuminaLearn API on the configured host and port: `python -m app` from backend/.

Reads BACKEND_HOST and BACKEND_PORT from .env, and refuses to start when that port is already
taken, instead of starting behind another program that would answer every request.
"""

import os
import sys

import uvicorn

from app.core.config import settings
from app.core.port_guard import port_in_use


def main() -> int:
    host, port = settings.BACKEND_HOST, settings.BACKEND_PORT
    if port_in_use(port):
        print(
            f"Port {port} is already in use by another program, so LuminaLearn cannot use it.\n"
            f"Stop that program, or set BACKEND_PORT to a free port in .env and BACKEND_URL in frontend/.env.local.",
            file=sys.stderr,
        )
        return 1
    os.environ["UVICORN_PORT"] = str(port)  # reload workers read it to run the port-ownership check
    reload = settings.ENVIRONMENT != "production" and "--no-reload" not in sys.argv
    uvicorn.run("app.main:app", host=host, port=port, reload=reload, reload_dirs=["app", "../ai", "../ml"] if reload else None)
    return 0


if __name__ == "__main__":
    sys.exit(main())
