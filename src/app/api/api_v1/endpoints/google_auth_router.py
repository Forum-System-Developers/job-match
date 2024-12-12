from fastapi import APIRouter, Depends
from starlette.requests import Request

from app.services.google_auth_service import auth_callback, login
from app.utils.processors import process_async_request

router = APIRouter()


@router.get("/login")
async def login_route():
    async def _login():
        return await login()

    return await process_async_request(
        get_entities_fn=_login,
        status_code=200,
        not_found_err_msg="Login route not found.",
    )


@router.get("/callback")
async def auth_callback_route(request: Request):
    async def _auth_callback():
        return await auth_callback(request)

    return await process_async_request(
        get_entities_fn=_auth_callback,
        status_code=200,
        not_found_err_msg="Auth callback route not found.",
    )
