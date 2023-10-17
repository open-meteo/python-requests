# Open-Meteo API Python Client

This ia an API client to get weather data from the [Open-Meteo Weather API](https://open-meteo.com) based on the Python library `requests`.

Instead of using JSON, the API client uses FlatBuffers to transfer data. Encoding data in FlatBuffers is more efficient for long time-series data. Data can be transferred to `numpy` or `pandas` using [Zero-Copy](https://en.wikipedia.org/wiki/Zero-copy) to analyze large amount of data quickly. The schema definition files can be in [GitHub open-meteo/sdk](https://github.com/open-meteo/sdk).

This library is primarily designed for data-scientists to process weather data. In combination with the [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) data from 1940 onwards can be analyzed quickly.

## Basic Usage

The following example gets an hourly temperature and precipitation forecast for Berlin. Additionally, the current temperature is retrieved. It is recommended to only specify the required weather variables.

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
```

Note 1: You can also supply a list of latitude and longitude coordinates to get data for multiple locations. The API will return a array of results, hence in this example, we only consider the first location with `result = results[0]`.

Note 2: Please note the function calls `()` for each attribute like `Latitude()`. Those function calls are necessary due to the FlatBuffers format to dynamically get data from an attribute without expensive parsing.

### NumPy

If you are using `NumPy` you can easily get hourly or daily data as `NumPy` array of type float.

```python
import numpy as np

hourly = result.Hourly()
time = hourly.Time()

timestamps = np.arange(time.Start(), time.End(), time.Interval())
temperature_2m = hourly.Temperature2m().ValuesAsNumpy()
precipitation = hourly.Precipitation().ValuesAsNumpy()
```

### Pandas

For `Pandas` you can prepare a data-frame from hourly data like follows:


```python
# Usage with Pandas Dataframes
import pandas as pd

hourly = result.Hourly()
time = hourly.Time()

date = pd.date_range(
    start=pd.to_datetime(time.Start(), unit="s"),
    end=pd.to_datetime(time.End(), unit="s"),
    freq=pd.Timedelta(seconds=time.Interval()),
    inclusive="left"
)
df = pd.DataFrame(
    data = {
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

### Caching Data

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

# TODO
- Document multi location/timeinterval usage
- Document FlatBuffers data structure
- Document time start/end/interval
- Document timezones behavior
- Document pressure level and upper level
- Document endpoints for air quality, etc
- Consider dedicated pandas library to convert responses quickly

# License
MIT
