"""
Boot FastApi app
"""

import logging
from urllib.parse import urljoin

from ecs_logging import StdlibFormatter
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.app.api.api_v1.api import api_router
from src.app.core.config import get_settings
# from src.app.sql_app.database import initialize_database


def _setup_cors(p_app: FastAPI) -> None:
    """
    Set all CORS enabled origins
    """
    if get_settings().BACKEND_CORS_ORIGINS:
        p_app.add_middleware(
            CORSMiddleware,
            allow_origins=[
                str(origin) for origin in get_settings().BACKEND_CORS_ORIGINS
            ],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


def _create_app() -> FastAPI:
    app_ = FastAPI(
        title=get_settings().PROJECT_NAME,
        openapi_url=urljoin(get_settings().API_V1_STR, "openapi.json"),
        version=get_settings().VERSION,
        docs_url="/swagger",
    )
    app_.include_router(
        api_router,
        prefix=get_settings().API_V1_STR,
    )
    return app_


def _setup_logger() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    ecs_handler = logging.StreamHandler()
    ecs_handler.setFormatter(StdlibFormatter())

    logger = logging.getLogger()
    logger.addHandler(ecs_handler)


app = _create_app()
_setup_cors(app)
_setup_logger()

# initialize_database()
