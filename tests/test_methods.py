"""Test client"""
from __future__ import annotations

import pytest
from openmeteo_sdk.Variable import Variable

import openmeteo_requests


def test_fetch_all():
    om = openmeteo_requests.Client()
    params = {
        "latitude": [52.54, 48.1, 48.4],
        "longitude": [13.41, 9.31, 8.5],
        "hourly": ["temperature_2m", "precipitation"],
        "start_date": "2023-08-01",
        "end_date": "2023-08-02",
        "models": "era5_seamless"
        # 'timezone': 'auto',
        # 'current': ['temperature_2m','precipitation'],
        # 'current_weather': 1,
    }

    responses = om.weather_api("https://archive-api.open-meteo.com/v1/archive", params=params)
    # responses = om.get("http://127.0.0.1:8080/v1/archive", params=params)
    assert len(responses) == 3
    response = responses[0]
    assert response.Latitude() == pytest.approx(52.5)
    assert response.Longitude() == pytest.approx(13.4)
    response = responses[1]
    assert response.Latitude() == pytest.approx(48.1)
    assert response.Longitude() == pytest.approx(9.3)
    response = responses[0]

    print(f"Coordinates {response.Latitude()}°E {response.Longitude()}°N {response.Elevation()} m asl")
    print(f"Timezone {response.Timezone()} {response.TimezoneAbbreviation()} {response.UtcOffsetSeconds()}")
    print(f"Generation time {response.GenerationTimeMilliseconds()} ms")

    hourly = response.Hourly()
    hourly_variables = list(map(lambda i: hourly.Variables(i), range(0, hourly.VariablesLength())))

    temperature_2m = next(filter(lambda x: x.Variable() == Variable.temperature and x.Altitude() == 2, hourly_variables))
    precipitation = next(filter(lambda x: x.Variable() == Variable.precipitation, hourly_variables))

    assert temperature_2m.ValuesLength() == 48
    assert precipitation.ValuesLength() == 48

    # print(temperature_2m.ValuesAsNumpy())
    # print(precipitation.ValuesAsNumpy())


def test_int_client():
    """
    This test is marked implicitly as an integration test because the name contains "_init_"
    https://docs.pytest.org/en/6.2.x/example/markers.html#automatically-adding-markers-based-on-test-names
    """
