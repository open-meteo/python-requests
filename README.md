# Open-Meteo Python API Client

An API client to get weather data from the Open-Meteo Weather API based on the Python library `requests`.

Instead of using JSON, the API client uses FlatBuffers to transfer data. Encoding data in FlatBuffers is more efficient for long time-series data. Data can be transferred to `numpy` or `pandas` using [Zero-Copy](https://en.wikipedia.org/wiki/Zero-copy) to analyze large amount of data quickly.

TODO:
- Document data structure
- Consider dedicated pandas library

## Basic Usage

```python
# pip install openmeteo-requests

import openmeteo_requests

om = openmeteo_requests.Client()
params = {
    "latitude": 52.54,
    "longitude": 13.41,
    "hourly": ["temperature_2m", "precipitation"],
    "current": ["temperature_2m"]
}

results = om.weather_api("https://api.open-meteo.com/v1/forecast", params=params)
result = results[0]

print(f"Coordinates {result.Latitude()}°E {result.Longitude()}°N {result.Elevation()} m asl")
print(f"Timezone {result.Timezone()} {result.TimezoneAbbreviation()} Offset={result.UtcOffsetSeconds()}s")

print(f"Current temperature is {result.Current().Temperature2m().Value() °C}")

# Accessing hourly forecasts as numpy arrays
hourly = result.Hourly()
temperature_2m = hourly.Temperature2m().ValuesAsNumpy()
precipitation = hourly.Temperature2m().ValuesAsNumpy()

# Usage with Pandas Dataframes
import pandas as pd
date = pd.date_range(
    start=pd.to_datetime(hourly.Time().Start(), unit="s"),
    end=pd.to_datetime(hourly.Time().End(), unit="s"),
    freq=pd.Timedelta(seconds=hourly.Time().Interval()),
    inclusive="left"
)
df = pd.DataFrame(
    data={
        "date": date,
        "temperature_2m": hourly.Temperature2m().ValuesAsNumpy(),
        "precipitation": hourly.Precipitation().ValuesAsNumpy()
    }
)
print(df)
#date  temperature_2m  precipitation
#0  2023-08-01 00:00:00       16.945999            1.7
#1  2023-08-01 01:00:00       16.996000            2.1
#2  2023-08-01 02:00:00       16.996000            1.0
#3  2023-08-01 03:00:00       16.846001            0.2
```

## Caching Data

If you are working with large amounts of data, caching data can make it easier to develop. You can pass a cached session from the library `requests-cache` to the Open-Meteo API client.

The following example stores all data indefinitely (`expire_after=-1`) in a SQLite database called `.cache.sqlite`. For more options read the [requests-cache documentation](https://pypi.org/project/requests-cache/).

Additionally, `retry-requests` to automatically retry failed API calls in case there has been any unexpected network or server error.

```python
# pip install openmeteo-requests
# pip install requests-cache retry-requests

import openmeteo_requests
import requests_cache
from retry_requests import retry

# Setup the Open-Meteo API client with a cache and retry mechanism
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
om = openmeteo_requests.Client(session=retry_session)

# Using the client object `om` will now cache all weather data
```

# License
MIT
