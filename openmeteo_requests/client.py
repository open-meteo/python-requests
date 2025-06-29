"""Open-Meteo API client based on the requests library"""

from __future__ import annotations

from collections.abc import MutableMapping
from functools import partial
from typing import Any

import niquests
from openmeteo_sdk.WeatherApiResponse import WeatherApiResponse
from typing_extensions import TypeAlias

from openmeteo_requests.exceptions import OpenMeteoRequestsError

ParamsType = MutableMapping[str, Any]
OpenWeatherResponseType: TypeAlias = WeatherApiResponse


class Client:
    """Open-Meteo API Client"""

    def __init__(self, session: niquests.Session | None = None) -> None:
        self.session = session or niquests.Session()
        self._response_cls = WeatherApiResponse

    def _request(
        self,
        url: str,
        params: ParamsType,
        method: str,
        verify: bool | str | None,
        **kwargs,
    ) -> list[OpenWeatherResponseType]:
        params["format"] = "flatbuffers"

        if method.upper() == "POST":
            response = self.session.post(
                url, data=params, verify=verify, **kwargs
            )
        else:
            response = self.session.get(
                url, params=params, verify=verify, **kwargs
            )

        if response.status_code in [400, 429]:
            response_body = response.json()
            raise OpenMeteoRequestsError(response_body)

        response.raise_for_status()

        data: bytes = response.content or b""
        messages = []
        total = len(data)
        pos = 0
        while pos < total:
            length = int.from_bytes(data[pos : pos + 4], byteorder="little")
            message = self._response_cls.GetRootAs(data, pos + 4)
            messages.append(message)
            pos += length + 4
        print(messages)
        return messages

    def weather_api(
        self,
        url: str,
        params: ParamsType,
        method: str = "GET",
        verify: bool | str | None = None,
        **kwargs,
    ) -> list[WeatherApiResponse]:
        """Get and decode as weather api"""
        return self._request(url, params, method, verify, **kwargs)

    def close(self) -> None:
        """Close the client."""
        self.session.close()


# pylint: disable=too-few-public-methods
class AsyncClient:
    """Asynchronous client for Open-Meteo API."""

    def __init__(self, session: niquests.AsyncSession | None = None) -> None:
        self._session = session or niquests.AsyncSession()
        self._closed: bool = False
        self._response_cls = WeatherApiResponse

    async def _request(
        self,
        url: str,
        params: ParamsType,
        method: str,
        verify: bool | str | None,
        **kwargs,
    ) -> list[OpenWeatherResponseType]:
        params["format"] = "flatbuffers"

        response: niquests.Response
        async with self._session as sess:
            method = method.upper()
            if method == "GET":
                meth = partial(
                    sess.get, url, params=params, verify=verify, **kwargs
                )
            if method == "POST":
                meth = partial(
                    sess.post, url, data=params, verify=verify, **kwargs
                )
            response = await meth()

        if response.status_code in [400, 429]:
            response_body = response.json()
            raise OpenMeteoRequestsError(response_body)

        response.raise_for_status()

        data: bytes = response.content or b""
        messages = []
        total = len(data)
        pos = 0
        while pos < total:
            length = int.from_bytes(data[pos : pos + 4], byteorder="little")
            message = self._response_cls.GetRootAs(data, pos + 4)
            messages.append(message)
            pos += length + 4
        return messages

    async def weather_api(
        self,
        url: str,
        params: ParamsType,
        method: str = "GET",
        verify: bool | str | None = None,
        **kwargs,
    ) -> list[WeatherApiResponse]:
        """Get and decode as weather api"""
        try:
            return await self._request(
                url, dict(params), method, verify, **kwargs
            )
        except Exception as e:
            msg = f"failed to request {url}: {e}"
            raise OpenMeteoRequestsError(msg) from e

    async def close(self) -> None:
        """Close the client."""
        if not self._closed:
            await self._session.close()
        self._closed = True
