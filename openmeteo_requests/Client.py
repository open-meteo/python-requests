"""Open-Meteo API client based on the requests library"""

from __future__ import annotations

from typing import TypeVar

import niquests as requests
from openmeteo_sdk.WeatherApiResponse import WeatherApiResponse

T = TypeVar("T")


class OpenMeteoRequestsError(Exception):
    """Open-Meteo Error"""


class Client:
    """Open-Meteo API Client"""

    def __init__(self, session: requests.Session | None = None):
        self.session = session or requests.Session()

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def _get(self, cls: type[T], url: str, params: any, method: str, verify: bool | str | None, **kwargs) -> list[T]:
        params["format"] = "flatbuffers"

        if method.upper() == "POST":
            response = self.session.request("POST", url, data=params, verify=verify, **kwargs)
        else:
            response = self.session.request("GET", url, params=params, verify=verify, **kwargs)

        if response.status_code in [400, 429]:
            response_body = response.json()
            raise OpenMeteoRequestsError(response_body)

        response.raise_for_status()

        data = response.content
        messages = []
        total = len(data)
        pos = int(0)
        while pos < total:
            length = int.from_bytes(data[pos : pos + 4], byteorder="little")
            message = cls.GetRootAs(data, pos + 4)
            messages.append(message)
            pos += length + 4
        return messages

    def weather_api(
        self, url: str, params: any, method: str = "GET", verify: bool | str | None = None, **kwargs
    ) -> list[WeatherApiResponse]:
        """Get and decode as weather api"""
        return self._get(WeatherApiResponse, url, params, method, verify, **kwargs)

    def __del__(self):
        """cleanup"""
        self.session.close()


# pylint: disable=too-few-public-methods
class AsyncClient:
    """Open-Meteo API Client"""

    def __init__(self, session: requests.AsyncSession | None = None):
        self.session = session or requests.AsyncSession()

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    async def _get(
        self,
        cls: type[T],
        url: str,
        params: any,
        method: str,
        verify: bool | str | None,
        **kwargs,
    ) -> list[T]:
        params["format"] = "flatbuffers"

        if method.upper() == "POST":
            response = await self.session.request("POST", url, data=params, verify=verify, **kwargs)
        else:
            response = await self.session.request("GET", url, params=params, verify=verify, **kwargs)

        if response.status_code in [400, 429]:
            response_body = response.json()
            raise OpenMeteoRequestsError(response_body)

        response.raise_for_status()

        data = response.content
        messages = []
        total = len(data)
        pos = 0
        while pos < total:
            length = int.from_bytes(data[pos : pos + 4], byteorder="little")
            message = cls.GetRootAs(data, pos + 4)
            messages.append(message)
            pos += length + 4
        return messages

    async def weather_api(
        self, url: str, params: any, method: str = "GET", verify: bool | str | None = None, **kwargs
    ) -> list[WeatherApiResponse]:
        """Get and decode as weather api"""
        return await self._get(WeatherApiResponse, url, params, method, verify, **kwargs)
