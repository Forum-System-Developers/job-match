import pytest
import requests
from fastapi import HTTPException

from app.utils.request_handlers import perform_http_request


def test_performHttpRequest_returns_json_response(mocker):
    # Arrange
    url = "http://example.com"
    method = "GET"
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"key": "value"}
    mock_requests = mocker.patch(
        "app.utils.request_handlers.requests.request", return_value=mock_response
    )

    # Act
    response = perform_http_request(method=method, url=url)

    # Assert
    mock_requests.assert_called_once_with(method=method, url=url)
    assert response == {"key": "value"}


def test_performHttpRequestRaises_http_exception_on_error_status(mocker):
    # Arrange
    url = "http://example.com"
    method = "GET"
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"detail": "Not found"}
    mock_requests = mocker.patch(
        "app.utils.request_handlers.requests.request", return_value=mock_response
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        perform_http_request(method=method, url=url)
    mock_requests.assert_called_once_with(method=method, url=url)
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Not found"


def test_performHttpRequest_raises_http_exception_on_request_exception(mocker):
    # Arrange
    url = "http://example.com"
    method = "GET"
    mock_requests = mocker.patch(
        "app.utils.request_handlers.requests.request",
        side_effect=requests.RequestException("Request failed"),
    )

    # Act & Assert
    with pytest.raises(HTTPException) as exc_info:
        perform_http_request(method=method, url=url)
    mock_requests.assert_called_once_with(method=method, url=url)
    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Request failed"


def test_performHttpRequest_returns_text_response(mocker):
    # Arrange
    url = "http://example.com"
    method = "GET"
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "text/plain"}
    mock_response.text = "plain text response"
    mock_requests = mocker.patch(
        "app.utils.request_handlers.requests.request", return_value=mock_response
    )

    # Act
    response = perform_http_request(method=method, url=url)

    # Assert
    mock_requests.assert_called_once_with(method=method, url=url)
    assert response == mock_response
