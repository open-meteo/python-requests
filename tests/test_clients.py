"""Test clients."""

from __future__ import annotations

from typing import Any

import pytest
from openmeteo_sdk.Variable import Variable

from openmeteo_requests import AsyncClient, Client, OpenMeteoRequestsError


@pytest.fixture
def client() -> Client:
    return Client()


@pytest.fixture
def async_client() -> AsyncClient:
    return AsyncClient()


@pytest.fixture
def url() -> str:
    return "https://archive-api.open-meteo.com/v1/archive"


_ParamsType = dict[str, Any]


@pytest.fixture
def params() -> _ParamsType:
    return {
        "latitude": [52.54, 48.1, 48.4],
        "longitude": [13.41, 9.31, 8.5],
        "hourly": ["temperature_2m", "precipitation"],
        "start_date": "2023-08-01",
        "end_date": "2023-08-02",
        "models": "era5_seamless",
        # 'timezone': 'auto',
        # 'current': ['temperature_2m','precipitation'],
        # 'current_weather': 1,
    }


class TestClient:
    def test_fetch_all(
        self, client: Client, url: str, params: _ParamsType
    ) -> None:
        responses = client.weather_api(url=url, params=params)

        assert len(responses) == 3
        response = responses[0]
        assert response.Latitude() == pytest.approx(52.5)
        assert response.Longitude() == pytest.approx(13.4)
        response = responses[1]
        assert response.Latitude() == pytest.approx(48.1)
        assert response.Longitude() == pytest.approx(9.3)
        response = responses[0]

        hourly = response.Hourly()
        hourly_variables = list(
            map(lambda i: hourly.Variables(i), range(hourly.VariablesLength()))
        )

        temperature_2m = next(
            filter(
                lambda x: x.Variable() == Variable.temperature
                and x.Altitude() == 2,
                hourly_variables,
            )
        )
        precipitation = next(
            filter(
                lambda x: x.Variable() == Variable.precipitation,
                hourly_variables,
            )
        )

        assert temperature_2m.ValuesLength() == 48
        assert precipitation.ValuesLength() == 48

    def test_client_close(
        self, client: Client, url: str, params: _ParamsType
    ) -> None:
        responses = client.weather_api(url=url, params=params)
        assert responses

        client.close()

        with pytest.raises(OpenMeteoRequestsError):
            client.weather_api(url=url, params=params)

        client.close()  # does not break - idempotency


@pytest.mark.asyncio
class TestAsyncClient:
    async def test_async_fetch_all(
        self, async_client: AsyncClient, url: str, params: _ParamsType
    ) -> None:
        responses = await async_client.weather_api(url=url, params=params)

        assert len(responses) == 3
        response = responses[0]
        assert response.Latitude() == pytest.approx(52.5)
        assert response.Longitude() == pytest.approx(13.4)
        response = responses[1]
        assert response.Latitude() == pytest.approx(48.1)
        assert response.Longitude() == pytest.approx(9.3)
        response = responses[0]

        hourly = response.Hourly()
        hourly_variables = list(
            map(lambda i: hourly.Variables(i), range(hourly.VariablesLength()))
        )

        temperature_2m = next(
            filter(
                lambda x: x.Variable() == Variable.temperature
                and x.Altitude() == 2,
                hourly_variables,
            )
        )
        precipitation = next(
            filter(
                lambda x: x.Variable() == Variable.precipitation,
                hourly_variables,
            )
        )

        assert temperature_2m.ValuesLength() == 48
        assert precipitation.ValuesLength() == 48

    async def test_async_client_close(
        self, async_client: AsyncClient, url: str, params: _ParamsType
    ) -> None:
        responses = await async_client.weather_api(url=url, params=params)
        assert responses

        await async_client.close()

        with pytest.raises(OpenMeteoRequestsError):
            await async_client.weather_api(url=url, params=params)

        await async_client.close()  # does not break - idempotency


def test_int_client():
    """This test is marked implicitly as an integration test because the name contains "_init_"
    https://docs.pytest.org/en/6.2.x/example/markers.html#automatically-adding-markers-based-on-test-names
    """
