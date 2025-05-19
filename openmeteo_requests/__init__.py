"""Open-Meteo api top level exposed interfaces."""

from __future__ import annotations

from openmeteo_requests.Client import AsyncClient, Client

__all__ = ["Client", "AsyncClient"]
