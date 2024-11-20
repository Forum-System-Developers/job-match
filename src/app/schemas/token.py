from pydantic import BaseModel


class Token(BaseModel):
    """
    Token schema for representing authentication tokens.

    Attributes:
        access_token (str): The access token used for authentication.
        refresh_token (str): The refresh token used to obtain a new access token.
        token_type (str): The type of the token, typically "bearer".
    """

    access_token: str
    refresh_token: str
    token_type: str


class AccessToken(BaseModel):
    """
    Access token schema for representing access tokens.

    Attributes:
        access_token (str): The access token used for authentication.
    """

    access_token: str
