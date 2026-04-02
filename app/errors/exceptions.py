class AppException(Exception):
    """Base exception for application errors."""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        fields: dict[str, str] | None = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.fields = fields
        super().__init__(message)


class NotFoundError(AppException):
    def __init__(self, resource: str, identifier: str | None = None):
        message = (
            f"{resource} with id '{identifier}' not found"
            if identifier
            else f"{resource} not found"
        )
        super().__init__(
            status_code=404,
            code=f"{resource.upper().replace(' ', '_')}_NOT_FOUND",
            message=message,
        )


class ConflictError(AppException):
    def __init__(self, message: str):
        super().__init__(status_code=409, code="CONFLICT", message=message)


class ForbiddenError(AppException):
    def __init__(self, message: str = "You do not have permission for this action"):
        super().__init__(status_code=403, code="FORBIDDEN", message=message)


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(status_code=401, code="UNAUTHENTICATED", message=message)


class BadRequestError(AppException):
    def __init__(self, message: str):
        super().__init__(status_code=400, code="BAD_REQUEST", message=message)


class InactiveAccountError(AppException):
    def __init__(self):
        super().__init__(
            status_code=403,
            code="ACCOUNT_INACTIVE",
            message="Your account has been deactivated",
        )
