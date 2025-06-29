"""Open-Meteo API."""

from __future__ import annotations

from openmeteo_requests.Client import AsyncClient, Client
from openmeteo_requests.exceptions import OpenMeteoRequestsError

__all__ = [
    "AsyncClient",
    "Client",
    "OpenMeteoRequestsError",
]
