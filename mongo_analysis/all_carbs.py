from datetime import datetime
from pymongo import MongoClient
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from utils.get_readings import getReadings


collection_name = 'Treatments'
gt = getReadings()
query = {'carbs': {'$exists': True}}
df = gt.get_data_from_collection(collection_name, query)


df['created_at'] = pd.to_datetime(df['created_at']) 

cutoff_date = pd.to_datetime('09/01/2022', utc=True)

df = df[df['created_at'] >= cutoff_date]

df['hour'] = df['created_at'].dt.hour
df['minute'] = df['created_at'].dt.minute
df['time'] = df['hour'] * 60 + df['minute']
df['hour_minute'] = df['created_at'].dt.strftime('%H:%M')
df['date_str'] = df['created_at'].dt.strftime('%d %m %Y')
df['day_name'] = df['created_at'].dt.day_name()

df.sort_values(by='time', inplace=True)

res_hour_minute = df.groupby('hour_minute')['carbs'].agg([
    ('min', 'min'),
    ('max', 'max'),
    ('mean', 'mean'),
    ('sum', 'sum'),
    ('25th_percentile', lambda x: x.quantile(0.25)),
    ('50th_percentile', lambda x: x.quantile(0.5)),
    ('75th_percentile', lambda x: x.quantile(0.75))
])

res_date_str = df.groupby('date_str')['carbs'].agg([
    ('min', 'min'),
    ('max', 'max'),
    ('mean', 'mean'),
    ('sum', 'sum'),
    ('25th_percentile', lambda x: x.quantile(0.25)),
    ('50th_percentile', lambda x: x.quantile(0.5)),
    ('75th_percentile', lambda x: x.quantile(0.75))
])

res_hour_minute = res_hour_minute.rolling(10).mean().reset_index()

fig, (ax1) = plt.subplots(1, 1, figsize=(10, 8))

############################################# Plot for res_date_str #############################################
res_date_str = res_date_str.reset_index() 

res_date_str['date_str'] = pd.to_datetime(res_date_str['date_str'], format='%d %m %Y')
res_date_str.sort_values(by='date_str', inplace=True)

ax1.plot(res_date_str['date_str'], res_date_str['sum'], label='Sum carbs per Day')



ax1.set_title('carbs per Date')
ax1.set_xlabel('Date')
ax1.set_ylabel('carbs')
ax1.legend()
ax1.grid(True) 

############################################# heatmap  #############################################
import calplot
import matplotlib.pyplot as plt

df_cal = res_date_str[['date_str', 'sum']]
values = df_cal.set_index('date_str')['sum']

# Create the calendar heatmap
fig, axes = calplot.calplot(
    values, 
    suptitle='Calendar Heatmap',
    cmap='bwr', 
    vmin=0, 
    vmax=df_cal['sum'].max()
)

plt.tight_layout()

cbar_ax = fig.axes[-1]
cbar_ax.set_position([0.9, 0.15, 0.015, 0.7]) 

plt.show()
