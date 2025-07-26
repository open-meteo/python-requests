"""Open-Meteo API client based on the requests library"""

from __future__ import annotations

from collections.abc import MutableMapping
from enum import Enum
from functools import partial
from typing import Any

import niquests
from openmeteo_sdk.WeatherApiResponse import WeatherApiResponse

_FLAT_BUFFERS_FORMAT = "flatbuffers"

ParamsType = MutableMapping[str, Any]


class OpenMeteoRequestsError(Exception):
    """Open-Meteo Error."""


class HTTPVerb(str, Enum):
    GET = "GET"
    POST = "POST"


def _process_response(
    response: niquests.Response,
    *,
    handler: type[WeatherApiResponse] = WeatherApiResponse,
) -> list[WeatherApiResponse]:
    data: bytes = response.content or b""
    messages = []
    total = len(data)
    pos, step = 0, 4
    while pos < total:
        message = handler.GetRootAs(data, pos + step)
        messages.append(message)
        length = int.from_bytes(data[pos : pos + step], byteorder="little")
        pos += length + step
    return messages


class Client:
    """Open-Meteo API Client"""

    def __init__(self, session: niquests.Session | None = None) -> None:
        self._session = session or niquests.Session()
        self._response_cls = WeatherApiResponse
        self._closed: bool | None = None

    def _request(
        self,
        url: str,
        method: str,
        params: ParamsType,
        *,
        verify: bool | str | None = None,
        **kwargs,
    ) -> list[WeatherApiResponse]:
        params["format"] = _FLAT_BUFFERS_FORMAT

        if method.upper() == HTTPVerb.GET:
            response = self._session.get(
                url, params=params, verify=verify, **kwargs
            )
        if method.upper() == HTTPVerb.POST:
            response = self._session.post(
                url, data=params, verify=verify, **kwargs
            )

        if response.status_code in [400, 429]:
            response_body = response.json()
            raise OpenMeteoRequestsError(response_body)

        response.raise_for_status()
        return _process_response(response=response, handler=self._response_cls)

    def weather_api(
        self,
        url: str,
        params: ParamsType,
        method: str = HTTPVerb.GET,
        *,
        verify: bool | str | None = None,
        **kwargs,
    ) -> list[WeatherApiResponse]:
        """Get and decode as weather api"""
        try:
            if self._closed:
                msg = "Unavailable connection"
                raise ConnectionError(msg)

            return self._request(
                url=url,
                method=method,
                params=dict(params),
                verify=verify,
                **kwargs,
            )
        except Exception as e:
            msg = f"failed to request {url!r}: {e}"
            raise OpenMeteoRequestsError(msg) from e

    def close(self) -> None:
        """Close the client."""
        # closing session may not be enough here (niquests)
        self._session.close()
        self._closed = True


# pylint: disable=too-few-public-methods
class AsyncClient:
    """Asynchronous client for Open-Meteo API."""

    def __init__(self, session: niquests.AsyncSession | None = None) -> None:
        self._session = session or niquests.AsyncSession()
        self._response_cls = WeatherApiResponse

    async def _request(
        self,
        url: str,
        method: str,
        params: ParamsType,
        *,
        verify: bool | str | None = None,
        **kwargs,
    ) -> list[WeatherApiResponse]:
        params["format"] = _FLAT_BUFFERS_FORMAT

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
        return _process_response(response=response, handler=self._response_cls)

    async def weather_api(
        self,
        url: str,
        params: ParamsType,
        method: str = HTTPVerb.GET,
        *,
        verify: bool | str | None = None,
        **kwargs,
    ) -> list[WeatherApiResponse]:
        """Get and decode as weather api"""
        try:
            return await self._request(
                url=url,
                method=method,
                params=dict(params),
                verify=verify,
                **kwargs,
            )
        except Exception as e:
            msg = f"failed to request {url!r}: {e}"
            raise OpenMeteoRequestsError(msg) from e

    async def close(self) -> None:
        """Close the client."""
        await self._session.close()
