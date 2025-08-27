# Open-Meteo API Python Client

This API client provides access to weather data from [Open-Meteo Weather API](https://open-meteo.com) based on the Python library `niquests` and compatible with the `requests` library.

A key feature is its use of FlatBuffers instead of JSON for data transfer. FlatBuffers are particularly efficient when dealing with large volumes of time-series data. The library supports [Zero-Copy](https://en.wikipedia.org/wiki/Zero-copy) data transfer, allowing you to seamlessly analyze data directly within `numpy`, `pandas`, or `polars` without performance overhead. Schema definitions are available on [GitHub open-meteo/sdk](https://github.com/open-meteo/sdk).

This library is aimed at data scientists who need to quickly process and analyze weather data, including historical data from 1940 onward through the [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api).

## Basic Usage

The following example gets an hourly forecast (temperature, wind speed, and precipitation) for Berlin, and also retrieves the current temperature and humidity. To improve efficiency, request only the necessary variables.

```python
# pip install openmeteo-requests

import openmeteo_requests

openmeteo = openmeteo_requests.Client()

# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 52.52,
	"longitude": 13.41,
	"hourly": ["temperature_2m", "precipitation", "wind_speed_10m"],
	"current": ["temperature_2m", "relative_humidity_2m"],
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# Process current data. The order of variables needs to be the same as requested.
current = response.Current()
current_temperature_2m = current.Variables(0).Value()
current_relative_humidity_2m = current.Variables(1).Value()

print(f"Current time: {current.Time()}")
print(f"Current temperature_2m: {current_temperature_2m}")
print(f"Current relative_humidity_2m: {current_relative_humidity_2m}")
```

or the same but using async/wait:

```python
# pip install openmeteo-requests

import openmeteo_requests

import asyncio

async def main():
	openmeteo = openmeteo_requests.AsyncClient()

	# Make sure all required weather variables are listed here
	# The order of variables in hourly or daily is important to assign them correctly below
	url = "https://api.open-meteo.com/v1/forecast"
	params = {
		"latitude": 52.52,
		"longitude": 13.41,
		"hourly": ["temperature_2m", "precipitation", "wind_speed_10m"],
		"current": ["temperature_2m", "relative_humidity_2m"],
	}
	responses = await openmeteo.weather_api(url, params=params)

	# Process first location. Add a for-loop for multiple locations or weather models
	response = responses[0]
	print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
	print(f"Elevation: {response.Elevation()} m asl")
	print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

	# Process current data. The order of variables needs to be the same as requested.
	current = response.Current()
	current_temperature_2m = current.Variables(0).Value()
	current_relative_humidity_2m = current.Variables(1).Value()

	print(f"Current time: {current.Time()}")
	print(f"Current temperature_2m: {current_temperature_2m}")
	print(f"Current relative_humidity_2m: {current_relative_humidity_2m}")

asyncio.run(main())
```

Note 1: To retrieve data for multiple locations, you can provide a list of latitude and longitude coordinates. The API will return an array of results, one for each location. In the examples, we only demonstrate processing data from the first location `response = responses[0]` for brevity. See [multiple locations & models](#multiple-locations--models) for more information.

Note 2: Due to the FlatBuffers data format, accessing each attribute, like `Latitude`, requires a function call (e.g., `Latitude()`). This approach allows for efficient data access without the need for expensive parsing.

### NumPy

When using `NumPy`, hourly or daily data is readily available as a `NumPy` array of floats.

```python
import numpy as np
from openmeteo_sdk.Variable import Variable

hourly = response.Hourly()
hourly_time = range(hourly.Time(), hourly.TimeEnd(), hourly.Interval())
hourly_variables = list(map(lambda i: hourly.Variables(i), range(0, hourly.VariablesLength())))

hourly_temperature_2m = next(
    filter(
        lambda x: x.Variable() == Variable.temperature and x.Altitude() == 2,
        hourly_variables
    )
).ValuesAsNumpy()
hourly_precipitation = next(
    filter(
        lambda x: x.Variable() == Variable.precipitation,
        hourly_variables
    )
).ValuesAsNumpy()
hourly_wind_speed_10m = next(
    filter(
        lambda x: x.Variable() == Variable.wind_speed and x.Altitude() == 10,
        hourly_variables
    )
).ValuesAsNumpy()
```

### Pandas

After using `NumPy` to create arrays for hourly data, you can use `Pandas` to create a DataFrame from hourly data like follows:

```python
import pandas as pd

hourly_data = {"date": pd.date_range(
    start = pd.to_datetime(hourly.Time(), unit = "s"),
    end = pd.to_datetime(hourly.TimeEnd(), unit = "s"),
    freq = pd.Timedelta(seconds = hourly.Interval()),
    inclusive = "left"
)}
hourly_data["temperature_2m"] = hourly_temperature_2m
hourly_data["precipitation"] = hourly_precipitation
hourly_data["wind_speed_10m"] = hourly_wind_speed_10m

hourly_dataframe_pd = pd.DataFrame(data = hourly_data)
print(hourly_dataframe_pd)
#                    date  temperature_2m  precipitation  wind_speed_10m
# 0   2024-06-21 00:00:00       17.437000            0.0        6.569383
# 1   2024-06-21 01:00:00       17.087000            0.0        6.151683
# 2   2024-06-21 02:00:00       16.786999            0.0        7.421590
# 3   2024-06-21 03:00:00       16.337000            0.0        5.154416
```

### Polars

Additionally, `Polars` can also be used to create a DataFrame from hourly data using the `NumPy` arrays created previously:

```python
import polars as pl
from datetime import datetime, timedelta, timezone

start = datetime.fromtimestamp(hourly.Time(), timezone.utc)
end = datetime.fromtimestamp(hourly.TimeEnd(), timezone.utc)
freq = timedelta(seconds = hourly.Interval())

hourly_dataframe_pl = pl.select(
    date = pl.datetime_range(start, end, freq, closed = "left"),
    temperature_2m = hourly_temperature_2m,
    precipitation = hourly_precipitation,
    wind_speed_10m = hourly_wind_speed_10m
)
print(hourly_dataframe_pl)
# ┌─────────────────────────┬────────────────┬───────────────┬────────────────┐
# │ date                    ┆ temperature_2m ┆ precipitation ┆ wind_speed_10m │
# │ ---                     ┆ ---            ┆ ---           ┆ ---            │
# │ datetime[μs, UTC]       ┆ f32            ┆ f32           ┆ f32            │
# ╞═════════════════════════╪════════════════╪═══════════════╪════════════════╡
# │ 2024-06-21 00:00:00 UTC ┆ 17.437         ┆ 0.0           ┆ 6.569383       │
# │ 2024-06-21 01:00:00 UTC ┆ 17.087         ┆ 0.0           ┆ 6.151683       │
# │ 2024-06-21 02:00:00 UTC ┆ 16.786999      ┆ 0.0           ┆ 7.42159        │
# │ 2024-06-21 03:00:00 UTC ┆ 16.337         ┆ 0.0           ┆ 5.154416       │
```

### Caching Data

For improved development speed and efficiency when working with large datasets, consider using caching. You can integrate the `requests-cache` library by passing a cached session to the Open-Meteo API client.

A recommended configuration is to cache data for one hour (`expire_after=3600`), though indefinite caching (`expire_after=-1`) is also supported. Cached data is stored in a local SQLite database named `.cache.sqlite`. For more detailed configuration options, please refer to the [requests-cache documentation](https://pypi.org/project/requests-cache/).

To further enhance reliability, especially when dealing with network instability, the `retry-requests` library automatically retries failed API calls due to unexpected network or server errors.

```python
# pip install openmeteo-requests
# pip install requests-cache retry-requests

import openmeteo_requests
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with a cache and retry mechanism
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Using the client object `openmeteo` will now cache all weather data
```

### Multiple Locations / Models

If you are requesting data for multiple locations or models, you’ll receive an array of results. To access all of the data, replace `response = responses[0]` with a loop that iterates through the responses array, allowing you to process each location or model’s data.

```python
...

params = {
	"latitude": [52.52, 50.1155],
	"longitude": [13.41, 8.6842],
	"hourly": "temperature_2m",
	"models": ["icon_global", "icon_eu"],
}

...

# Process 2 locations and 2 models
for response in responses:
	print(f"\nCoordinates: {response.Latitude()}°N {response.Longitude()}°E")
	print(f"Elevation: {response.Elevation()} m asl")
	print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")
	print(f"Model Nº: {response.Model()}")

	...
```

## TODO

- Document FlatBuffers data structure
- Document time start/end/interval
- Document timezones behavior
- Document pressure level and upper level
- Document endpoints for air quality, etc
- Consider dedicated pandas library to convert responses quickly

## License

MIT
