"""Open-Meteo API."""

from __future__ import annotations

from openmeteo_requests.Client import (
    AsyncClient,
    Client,
    OpenMeteoRequestsError,
)

__all__ = [
    "AsyncClient",
    "Client",
    "OpenMeteoRequestsError",
]
