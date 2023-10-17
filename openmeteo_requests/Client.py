"""Open-Meteo API client based on the requests library"""

from __future__ import annotations

from typing import TypeVar

import requests
from openmeteo_sdk.AirQualityApiResponse import AirQualityApiResponse
from openmeteo_sdk.ClimateApiResponse import ClimateApiResponse
from openmeteo_sdk.EnsembleApiResponse import EnsembleApiResponse
from openmeteo_sdk.FloodApiResponse import FloodApiResponse
from openmeteo_sdk.MarineApiResponse import MarineApiResponse
from openmeteo_sdk.WeatherApiResponse import WeatherApiResponse

T = TypeVar("T")
TSession = TypeVar("TSession", bound=requests.Session)


class OpenMeteoRequestsError(Exception):
    """Open-Meteo Error"""


class Client:
    """Open-Meteo API Client"""

    def __init__(self, session: TSession | None = None):
        self.session = session or requests.Session()

    def _get(self, cls: type[T], url: str, params: any) -> list[T]:
        params["format"] = "flatbuffers"

        response = self.session.get(url, params=params)
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

    def weather_api(self, url: str, params: any) -> list[WeatherApiResponse]:
        """Get and decode as weather api"""
        return self._get(WeatherApiResponse, url, params)

    def ensemble_api(self, url: str, params: any) -> list[EnsembleApiResponse]:
        """Get and decode as ensemble api"""
        return self._get(EnsembleApiResponse, url, params)

    def flood_api(self, url: str, params: any) -> list[FloodApiResponse]:
        """Get and decode as flood api"""
        return self._get(FloodApiResponse, url, params)

    def air_quality_api(self, url: str, params: any) -> list[AirQualityApiResponse]:
        """Get and decode as air quality api"""
        return self._get(AirQualityApiResponse, url, params)

    def climate_api(self, url: str, params: any) -> list[ClimateApiResponse]:
        """Get and decode as climate api"""
        return self._get(ClimateApiResponse, url, params)

    def marine_api(self, url: str, params: any) -> list[MarineApiResponse]:
        """Get and decode as marine api"""
        return self._get(MarineApiResponse, url, params)

    def __del__(self):
        """cleanup"""
        self.session.close()
