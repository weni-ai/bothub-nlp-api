from fastapi import HTTPException


class CeleryTimeoutException(HTTPException):
    def __init__(
        self, headers: dict = None,
    ) -> None:
        detail = f"There was an error parsing the sentence. Check the details: Time limit exceeded"
        super().__init__(status_code=503, detail=detail)
        self.headers = headers
