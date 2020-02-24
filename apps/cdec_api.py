"""
Summary
-------
A python module to request time series data from the California Data Exchange
Center (CDEC) [1]_.

Example
-------
Below is an example of how to obtain the Sacramento at Freeport hourly flow
data for the month of September 2019 and feed it into a `pandas` DataFrame.

>>> import cdec_api as cdec
>>> import pandas as pd
>>> data = cdec.main(stations='FPT', sensor_id=20, duration='H',
...                  start_date='2019-09-01', end_date='2019-09-30')
>>> df = pd.read_json(data, orient='records')
>>> df.head()
   SENSOR_NUM dataFlag                date durCode        obsDate sensorType stationId units  value
0          20          2019-09-01 00:00:00       H  2019-9-1 0:00       FLOW       FPT   CFS  22213
1          20          2019-09-01 01:00:00       H  2019-9-1 1:00       FLOW       FPT   CFS  22889
2          20          2019-09-01 02:00:00       H  2019-9-1 2:00       FLOW       FPT   CFS  22987
3          20          2019-09-01 03:00:00       H  2019-9-1 3:00       FLOW       FPT   CFS  22987
4          20          2019-09-01 04:00:00       H  2019-9-1 4:00       FLOW       FPT   CFS  21926

Notes
-----
The following notes are reserved for future development:
1. Include `argparse` functionality similar to `run_CalSim.py`.

References
----------
The references below are formatted according to Chicago Manual of Style, 16th
Edition.

.. [1] California, State of. “WELCOME TO CALIFORNIA DATA EXCHANGE CENTER.”
   California Data Exchange Center - Query Tools. Accessed October 2, 2019.
   http://cdec.water.ca.gov/.

"""
# %% Import libraries.
import requests


# %% Define Functions.
def main(stations, sensor_id, duration,
         start_date='1969-10-31', end_date='2015-09-30'):
    """
    Summary
    -------
    Query station data from CDEC and return a string in json 'records' format.

    Parameters
    ----------
    stations : str or list of str
        CDEC Station ID. See CDEC Station Map [1]_ for available Station IDs.
    sensor_id : int
        Station Sensor ID. Below are some common CDEC Sensor IDs.

        - 1 : RIVER STAGE
        - 20 : FLOW, RIVER DISCHARGE
        - 25 : TEMPERATURE, WATER
        - 41 : FLOW, MEAN DAILY
        - 70 : DISCHARGE, PUMPING
        - 100 : ELECTRICAL CONDUCTIVITY

    duration : str
        Duration code of data timestep. Below are some examples.

        - 'D' : Daily
        - 'H' : Hourly
        - 'E' : Event

    start_date : str, default '1969-10-31', optional
        Start date of query time frame in ISO 8601 format.
    end_date : str, default '2015-09-30', optional
        End date of query time frame in ISO 8601 format.

    References
    ----------
    The references below are formatted according to Chicago Manual of Style, 16th
    Edition.

    .. [1] California Data Exchange Center - Query Tools. Accessed October 2,
       2019. http://cdec.water.ca.gov/cdecstation2/.

    """
    # Initialize variables.
    cdec_daily_url = 'http://cdec.water.ca.gov/dynamicapp/req/JSONDataServlet'
    if isinstance(stations, list):
        stations = '%2C'.join(stations)
    elif isinstance(stations, str):
        pass
    else:
        msg = 'Variable `stations` must be string or list object.'
        raise TypeError(msg)
    payload = {'Stations': stations,
               'SensorNums': sensor_id,
               'dur_code': duration,
               'Start': start_date,
               'End': end_date}
    # Query data.
    r = requests.get(cdec_daily_url, params=payload)
    data = r.text
    # Clean data.
    data = data.replace('\r', '')
    # Return data as string in json format.
    return data


# %% Execute script.
if __name__ == '__main__':
    msg = ('This script is intended for import into another module and is not'
           ' meant to be run as a __main__ file.')
    raise RuntimeError(msg)
