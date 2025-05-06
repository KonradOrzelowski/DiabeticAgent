from datetime import datetime
from pymongo import MongoClient
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from utils.get_readings import getReadings


DEFAULT_TIMEZONE_OFFSET_HOURS = 5
DEFAULT_COLLECTION_NAME = 'Entries'



def get_night_stats(end_day: str, time_range_days: int, last_night_hour: int) -> pd.DataFrame:
    """
    Computes nightly statistics of glucose readings between specific hours over a given date range.

    Args:
        end_day (str): The end date in 'YYYY-MM-DD' format.
        time_range_days (int): How many days back to consider.
        last_night_hour (int): Last hour considered as 'night' (e.g., 7 for 7 AM).

    Returns:
        pd.DataFrame: Nighttime statistics (min, max, mean, quartiles) grouped by date.
    """

    gt = getReadings()

    start_day = pd.Timestamp(end_day) - pd.Timedelta(time_range_days, "d")


    t_start_day = pd.Timestamp(start_day) - pd.Timedelta(DEFAULT_TIMEZONE_OFFSET_HOURS, "h")
    t_end_day = pd.Timestamp(end_day) + pd.Timedelta(DEFAULT_TIMEZONE_OFFSET_HOURS, "h")


    query = {
        'sgv': {
            '$exists': True
        },
        'dateString': {
            '$gte': t_start_day.isoformat(),
            '$lte': t_end_day.isoformat()
        }
    }
    df = gt.get_data_from_collection(DEFAULT_COLLECTION_NAME, query)
    print(df)
    if df.empty:
        return pd.DataFrame()

    df['date'] = df['created_at'].dt.date

    df = df.set_index('created_at')
    df_night_hours = df.between_time('00:00', f'{last_night_hour}:00')




    stats_night_hours = df_night_hours.groupby(['date'])['sgv'].agg([
        ('min', 'min'),
        ('max', 'max'),
        ('mean', 'mean'),
        ('25th_per', lambda x: x.quantile(0.25)),
        ('50th_per', lambda x: x.quantile(0.5)),
        ('75th_per', lambda x: x.quantile(0.75))
    ]).round(2)

    return stats_night_hours

end_day = '2024-10-08'
time_range_days = 14
last_night_hour = 7
df = get_night_stats(end_day, time_range_days, last_night_hour)

print(df.to_markdown())
