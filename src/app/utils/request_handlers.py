import requests
from fastapi import HTTPException


def perform_http_request(method: str, url: str, **kwargs):
    """
    Perform an HTTP request using the specified method and URL.

    Args:
        method (str): The HTTP method to use for the request (e.g., 'GET', 'POST').
        url (str): The URL to which the request is sent.
        **kwargs: Additional arguments passed to the `requests.request` function.

    Returns:
        dict: The JSON response from the server.

    Raises:
        HTTPException: If the response status code indicates an error (400-599) or if a request exception occurs.
    """
    try:
        response = requests.request(method=method, url=url, **kwargs)
        if 400 <= response.status_code < 600:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.json().get("detail"),
            )
        return response.json()
    except requests.RequestException as e:
        raise HTTPException(
            status_code=response.status_code if response else 500,
            detail=str(e),
        )


def perform_get_request(url: str, **kwargs):
    """
    Perform an HTTP GET request to the specified URL.

    Args:
        url (str): The URL to send the GET request to.
        **kwargs: Additional keyword arguments to pass to the HTTP request.

    Returns:
        Response: The response object resulting from the GET request.
    """
    return perform_http_request("GET", url, **kwargs)


def perform_post_request(url: str, **kwargs):
    """
    Perform an HTTP POST request to the specified URL with the given parameters.

    Args:
        url (str): The URL to which the POST request is sent.
        **kwargs: Additional keyword arguments to pass to the request.

    Returns:
        Response: The response object resulting from the POST request.
    """
    return perform_http_request("POST", url, **kwargs)


def perform_put_request(url: str, **kwargs):
    """
    Perform an HTTP PUT request to the specified URL.

    Args:
        url (str): The URL to which the PUT request is sent.
        **kwargs: Additional keyword arguments to pass to the request.

    Returns:
        Response: The response object resulting from the PUT request.
    """
    return perform_http_request("PUT", url, **kwargs)


def perform_delete_request(url: str, **kwargs):
    """
    Perform an HTTP DELETE request to the specified URL.

    Args:
        url (str): The URL to which the DELETE request is sent.
        **kwargs: Additional keyword arguments to pass to the HTTP request.

    Returns:
        Response: The response object resulting from the DELETE request.
    """
    return perform_http_request("DELETE", url, **kwargs)
