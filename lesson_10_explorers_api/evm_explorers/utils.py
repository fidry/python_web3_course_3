from curl_cffi.requests import AsyncSession
from evm_explorers import exceptions


def aiohttp_params(params: dict[str, ...] | None) -> dict[str, str | int | float] | None:
    new_params = params.copy()
    if not params:
        return

    for key, value in params.items():
        if value is None:
            del new_params[key]

        if isinstance(value, bool):
            new_params[key] = str(value).lower()

        elif isinstance(value, bytes):
            new_params[key] = value.decode('utf-8')

    return new_params


async def async_get(url: str, headers: dict | None = None, **kwargs) -> dict | None:
    async with AsyncSession() as session:
        response = await session.get(url, headers=headers, **kwargs)
        status_code = response.status_code

        if status_code <= 201:
            return response.json()

        raise exceptions.HTTPException(response=response.text, status_code=status_code)
