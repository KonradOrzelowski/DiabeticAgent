from datetime import datetime
from pymongo import MongoClient
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from utils.get_readings import getReadings

def process_dataframe(df, column_to_agg, date_str = '09/01/2022', is_utc = True):

    df['created_at'] = pd.to_datetime(df['created_at']) 

    cutoff_date = pd.to_datetime(date_str, utc=is_utc)

    df = df[df['created_at'] >= cutoff_date].copy()

    df['hour'] = df['created_at'].dt.hour
    df['minute'] = df['created_at'].dt.minute
    df['time'] = df['hour'] * 60 + df['minute']
    df['hour_minute'] = df['created_at'].dt.strftime('%H:%M')
    df['date_str'] = df['created_at'].dt.strftime('%d %m %Y')
    df['day_name'] = df['created_at'].dt.day_name()

    df.sort_values(by='time', inplace=True)

    res_date_str = df.groupby('date_str')[column_to_agg].agg([
        ('min', 'min'),
        ('max', 'max'),
        ('mean', 'mean'),
        ('sum', 'sum'),
        ('25th_percentile', lambda x: x.quantile(0.25)),
        ('50th_percentile', lambda x: x.quantile(0.5)),
        ('75th_percentile', lambda x: x.quantile(0.75))
    ])

    return res_date_str

############################################################################################
collection_name = 'Treatments'
gt = getReadings()
query = {'carbs': {'$exists': True}}
df_carbs = gt.get_data_from_collection(collection_name, query)
df_carbs = df_carbs[['created_at', 'carbs']]
df_carbs['date_str'] = df_carbs['created_at'].dt.strftime('%d %m %Y')

############################################################################################
collection_name = 'Entries'
gt = getReadings()
query = {'sgv': {'$exists': True}}
df_sgv = gt.get_data_from_collection(collection_name, query)
df_sgv = df_sgv[['created_at', 'sgv']]
df_sgv['date_str'] = df_sgv['created_at'].dt.strftime('%d %m %Y')

############################################################################################
import pandas as pd
from datetime import timedelta
def get_fasting_impact(df_carbs_, df_sgv_, date, hours=5):
    df_carbs = df_carbs_[df_carbs_.date_str == date].copy()
    df_sgv = df_sgv_[df_sgv_.date_str == date].copy()

    if df_carbs.empty or df_sgv.empty:
        return [date, None, None, None, None, None, None]

    df_carbs['created_at'] = pd.to_datetime(df_carbs['created_at'])
    df_sgv['created_at'] = pd.to_datetime(df_sgv['created_at'])

    df_carbs = df_carbs.sort_values('created_at').reset_index(drop=True)

    fasting_periods = []
    last_carb_time = None

    for idx, row in df_carbs.iterrows():
        if row['carbs'] > 0:
            if last_carb_time is not None:
                delta = row['created_at'] - last_carb_time
                if delta.total_seconds() >= hours * 3600:
                    fasting_periods.append((last_carb_time + timedelta(hours=hours), row['created_at']))
            last_carb_time = row['created_at']

    fasting_lst = []
    carbs_lst = []

    for start, end in fasting_periods:
        fasting_segment = df_sgv[(df_sgv.created_at > start) & (df_sgv.created_at < end)]
        non_fasting_segment = df_sgv[~((df_sgv.created_at > start) & (df_sgv.created_at < end))]
        if not fasting_segment.empty:
            fasting_lst.append(fasting_segment)
        if not non_fasting_segment.empty:
            carbs_lst.append(non_fasting_segment)

    if fasting_lst:
        fating_df = pd.concat(fasting_lst).drop_duplicates()
        fasting_stats = [date, fating_df.sgv.mean(), fating_df.sgv.min(), fating_df.sgv.max()]
    else:
        return [date, None, None, None, df_sgv.sgv.mean(), df_sgv.sgv.min(), df_sgv.sgv.max()]

    if carbs_lst:
        carbs_df = pd.concat(carbs_lst).drop_duplicates()
        carbs_stats = [carbs_df.sgv.mean(), carbs_df.sgv.min(), carbs_df.sgv.max()]
    else:
        carbs_stats = [None, None, None]

    return fasting_stats + carbs_stats


    
# print()

lst = []
for day in list(set(df_sgv['date_str'])):
    stats = get_fasting_impact(df_carbs, df_sgv, date = day, hours = 5)
    lst.append(stats)
df = pd.DataFrame(lst, columns = ['date_str', 'fasting_mean', 'fasting_min', 'fasting_max', 'carbs_mean', 'carbs_min', 'carbs_max'])
df['date'] = pd.to_datetime(df['date_str'], format='%d %m %Y')

import calplot
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

colors = ['deepskyblue', 'lawngreen', 'orangered']
cmap = LinearSegmentedColormap.from_list('bgr_custom', colors, N=256)

def plot_calendar_heatmap(df, column_name, title):
    if not isinstance(df.index, pd.DatetimeIndex):
        df = df.reset_index()

    df['date'] = pd.to_datetime(df['date_str'], format='%d %m %Y')
    df.set_index('date', inplace=True)

    values = df[column_name]

    fig, axes = calplot.calplot(
        values,
        cmap=cmap,
        colorbar=False,
        vmin=values.quantile(0.1),
        vmax=values.quantile(0.9)
    )

    fig.suptitle(title, fontsize=16)

    norm = plt.Normalize(vmin=values.quantile(0.1), vmax=values.quantile(0.9))
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])  
    cbar = fig.colorbar(sm, cax=cbar_ax)
    cbar.set_label(column_name, rotation=270, labelpad=15)

    fig.tight_layout(rect=[0, 0, 0.9, 0.95])  #



    

# Plot for total insulin
plot_calendar_heatmap(df, 'fasting_mean', 'fasting_mean')

# Plot for carbs
plot_calendar_heatmap(df, 'carbs_mean', 'carbs_mean')

plt.show()
