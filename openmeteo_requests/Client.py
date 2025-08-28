"""Open-Meteo API client based on the requests library"""

from __future__ import annotations

from collections.abc import MutableMapping
from enum import Enum
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
        length = int.from_bytes(data[pos : pos + step], byteorder="little")
        # In stream error messages start with "Unexpected"
        if length == 0x78656E55:
            raise OpenMeteoRequestsError(data[pos:total].decode("utf-8"))
        message = handler.GetRootAs(data, pos + step)
        messages.append(message)
        pos += length + step
    return messages


class Client:
    """Open-Meteo API Client"""

    def __init__(self, session: niquests.Session | None = None) -> None:
        self._close_session = session is None
        self._session = session or niquests.Session()

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

        method = method.upper()
        if method == HTTPVerb.POST:
            response = self._session.post(url, data=params, verify=verify, **kwargs)
        else:
            response = self._session.get(url, params=params, verify=verify, **kwargs)

        if response.status_code in [400, 429]:
            response_body = response.json()
            raise OpenMeteoRequestsError(response_body)

        response.raise_for_status()
        return _process_response(response=response, handler=WeatherApiResponse)

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

    def __del__(self):
        """cleanup"""
        if self._close_session:
            self._session.close()


# pylint: disable=too-few-public-methods
class AsyncClient:
    """Asynchronous client for Open-Meteo API."""

    def __init__(self, session: niquests.AsyncSession | None = None) -> None:
        self._session = session

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

        method = method.upper()
        if method == HTTPVerb.POST:
            if self._session:
                response = await self._session.post(url, data=params, verify=verify, **kwargs)
            else:
                response = await niquests.apost(url, data=params, verify=verify, **kwargs)
        else:
            if self._session:
                response = await self._session.get(url, params=params, verify=verify, **kwargs)
            else:
                response = await niquests.aget(url, params=params, verify=verify, **kwargs)

        if response.status_code in [400, 429]:
            response_body = response.json()
            raise OpenMeteoRequestsError(response_body)

        response.raise_for_status()
        return _process_response(response=response, handler=WeatherApiResponse)

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
