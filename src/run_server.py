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
        default=8080,
        help="port to listen on (default: 8080)",
    )
    config = parser.parse_args()

    reload_dirs = config.reload.split(",") if config.reload else []
    reload_enabled = bool(reload_dirs)

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=config.port,
        reload=reload_enabled,
        reload_dirs=reload_dirs,
    )
