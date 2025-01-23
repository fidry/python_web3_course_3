class APIException(Exception):
    pass


class HTTPException(Exception):
    response: dict[str, ...] | None
    status_code: int | None

    def __init__(self, response: dict[str, ...] | None = None, status_code: int | None = None) -> None:
        self.response = response
        self.status_code = status_code

    def __str__(self):
        if self.response:
            return f'{self.status_code}: {self.response}'

        return f'{self.status_code}'
