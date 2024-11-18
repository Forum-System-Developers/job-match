"""
Entry point for running server
"""
#!/usr/bin/env python3

from argparse import ArgumentParser

import uvicorn

config = None

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "-r",
        "--reload",
        metavar="DIRS",
        default=None,
        help="enable auto-reloading of this base dir (e.g. '--reload src/'); "
        "also enabled DEBUG mode",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=8000,
        help="port to listen on (default: 8000)",
    )
    config = parser.parse_args()

    reload_dirs = config.reload.split(",") if config.reload else []
    reload_enabled = bool(reload_dirs)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=config.port,
        reload=True,
        reload_dirs=reload_dirs,
    )
