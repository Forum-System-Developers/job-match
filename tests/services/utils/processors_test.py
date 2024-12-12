import json

import pytest
from fastapi import status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from app.exceptions.custom_exceptions import ApplicationError
from app.utils.processors import (
    _format_response,
    process_async_request,
    process_request,
)


def test_process_request_returnsSuccessfulResponse_whenDataIsValid(mocker) -> None:
    # Arrange
    get_entities_fn = mocker.Mock(return_value={"key": "value"})
    status_code = status.HTTP_200_OK
    not_found_err_msg = "Entity not found"

    # Act
    response = process_request(
        get_entities_fn=get_entities_fn,
        status_code=status_code,
        not_found_err_msg=not_found_err_msg,
    )

    # Assert
    assert response.status_code == status_code
    assert json.loads(response.body) == {"detail": {"key": "value"}}
    get_entities_fn.assert_called_once()


def test_processRequest_handlesApplicationError(mocker) -> None:
    # Arrange
    get_entities_fn = mocker.Mock(
        side_effect=ApplicationError(
            detail="Entity not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    )
    status_code = status.HTTP_200_OK
    not_found_err_msg = "Entity not found"

    # Act
    response = process_request(
        get_entities_fn=get_entities_fn,
        status_code=status_code,
        not_found_err_msg=not_found_err_msg,
    )

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert json.loads(response.body) == {"detail": {"error": "Entity not found"}}
    get_entities_fn.assert_called_once()


def test_process_request_handlesTypeError(mocker) -> None:
    # Arrange
    get_entities_fn = mocker.Mock(side_effect=TypeError("Type error occurred"))
    status_code = status.HTTP_200_OK
    not_found_err_msg = "Entity not found"

    # Act
    response = process_request(
        get_entities_fn=get_entities_fn,
        status_code=status_code,
        not_found_err_msg=not_found_err_msg,
    )

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert json.loads(response.body) == {"detail": {"error": "Type error occurred"}}
    get_entities_fn.assert_called_once()


def test_processRequest_handlesSyntaxError(mocker) -> None:
    # Arrange
    get_entities_fn = mocker.Mock(side_effect=SyntaxError("Syntax error occurred"))
    status_code = status.HTTP_200_OK
    not_found_err_msg = "Entity not found"

    # Act
    response = process_request(
        get_entities_fn=get_entities_fn,
        status_code=status_code,
        not_found_err_msg=not_found_err_msg,
    )

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.body) == {"detail": {"error": "Syntax error occurred"}}
    get_entities_fn.assert_called_once()


@pytest.mark.asyncio
async def test_processAsyncRequest_returnsSuccessfulResponse_whenDataIsValid(
    mocker,
) -> None:
    # Arrange
    get_entities_fn = mocker.AsyncMock(return_value={"key": "value"})
    status_code = status.HTTP_200_OK
    not_found_err_msg = "Entity not found"

    # Act
    response = await process_async_request(
        get_entities_fn=get_entities_fn,
        status_code=status_code,
        not_found_err_msg=not_found_err_msg,
    )

    # Assert
    assert response.status_code == status_code
    assert json.loads(response.body) == {"detail": {"key": "value"}}
    get_entities_fn.assert_called_once()


@pytest.mark.asyncio
async def test_processAsyncRequest_handlesApplicationError(mocker) -> None:
    # Arrange
    get_entities_fn = mocker.AsyncMock(
        side_effect=ApplicationError(
            detail="Entity not found",
            status_code=status.HTTP_404_NOT_FOUND,
        )
    )
    status_code = status.HTTP_200_OK
    not_found_err_msg = "Entity not found"

    # Act
    response = await process_async_request(
        get_entities_fn=get_entities_fn,
        status_code=status_code,
        not_found_err_msg=not_found_err_msg,
    )

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert json.loads(response.body) == {"detail": {"error": "Entity not found"}}
    get_entities_fn.assert_called_once()


@pytest.mark.asyncio
async def test_processAsyncRequest_handlesTypeError(mocker) -> None:
    # Arrange
    get_entities_fn = mocker.AsyncMock(side_effect=TypeError("Type error occurred"))
    status_code = status.HTTP_200_OK
    not_found_err_msg = "Entity not found"

    # Act
    response = await process_async_request(
        get_entities_fn=get_entities_fn,
        status_code=status_code,
        not_found_err_msg=not_found_err_msg,
    )

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert json.loads(response.body) == {"detail": {"error": "Type error occurred"}}
    get_entities_fn.assert_called_once()


@pytest.mark.asyncio
async def test_processAsyncRequest_handlesSyntaxError(mocker) -> None:
    # Arrange
    get_entities_fn = mocker.AsyncMock(side_effect=SyntaxError("Syntax error occurred"))
    status_code = status.HTTP_200_OK
    not_found_err_msg = "Entity not found"

    # Act
    response = await process_async_request(
        get_entities_fn=get_entities_fn,
        status_code=status_code,
        not_found_err_msg=not_found_err_msg,
    )

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert json.loads(response.body) == {"detail": {"error": "Syntax error occurred"}}
    get_entities_fn.assert_called_once()


@pytest.mark.asyncio
async def test_processAsyncRequest_handlesRedirectResponse(mocker) -> None:
    # Arrange
    redirect_url = "http://example.com"
    get_entities_fn = mocker.AsyncMock(return_value=RedirectResponse(url=redirect_url))
    status_code = status.HTTP_200_OK
    not_found_err_msg = "Entity not found"

    # Act
    response = await process_async_request(
        get_entities_fn=get_entities_fn,
        status_code=status_code,
        not_found_err_msg=not_found_err_msg,
    )

    # Assert
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"] == redirect_url
    get_entities_fn.assert_called_once()


def test_formatResponse_withSingleModel() -> None:
    # Arrange
    class MockModel(BaseModel):
        key: str

    data = MockModel(key="value")

    # Act
    result = _format_response(data)

    # Assert
    assert result == {"detail": {"key": "value"}}


def test_formatResponse_withListOfModels() -> None:
    # Arrange
    class MockModel(BaseModel):
        key: str

    data = [MockModel(key="value1"), MockModel(key="value2")]

    # Act
    result = _format_response(data)

    # Assert
    assert result == {"detail": [{"key": "value1"}, {"key": "value2"}]}


def test_formatResponse_withDict(mocker) -> None:
    # Arrange
    data = {"key": "value"}

    # Act
    result = _format_response(data)

    # Assert
    assert result == {"detail": {"key": "value"}}
