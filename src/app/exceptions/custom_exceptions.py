class ApplicationError(Exception):
    def __init__(self, detail: str = "An error occurred"):
        self.detail = detail
        super().__init__(self.detail)


class BadRequest(ApplicationError):
    def __init__(self, detail: str = "Bad request"):
        super().__init__(detail)


class Unauthorized(ApplicationError):
    def __init__(self, detail: str = "Unauthorized access"):
        super().__init__(detail)


class Forbidden(ApplicationError):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(detail)


class NotFound(ApplicationError):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail)
