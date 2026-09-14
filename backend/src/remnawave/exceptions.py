from fastapi.exceptions import HTTPException
from fastapi import status


class RemnaWaveNotFoundError(HTTPException):
    def __init__(
        self,
        detail: str = "Not found"
    ) -> None:
        self.status_code = status.HTTP_404_NOT_FOUND
        self.detail = detail
