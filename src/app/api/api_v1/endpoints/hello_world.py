# """
# SHOP DEVIATION REST API
# """
# import logging
# from typing import Union

# from fastapi import APIRouter
# from fastapi.responses import JSONResponse


# MIME_TYPE_APP_JSON = "application/json"

# router = APIRouter()

# logger = logging.getLogger(__name__)


# @router.get("/", response_model=str)
# async def hello_world() -> Union[str, JSONResponse]:
#     """
#     Return the article deviations for specific article in camelCase
#     """
#     return JSONResponse(
#         content={"message": "Hello World"},
#         media_type=MIME_TYPE_APP_JSON,
#     )
