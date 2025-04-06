from datetime import datetime
from pymongo import MongoClient
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from utils.get_readings import getReadings

collection_name = 'Entries'
gt = getReadings()
query = {'sgv': {'$exists': True}}
df = gt.get_data_from_collection(collection_name, query)


df['created_at'] = pd.to_datetime(df['created_at']) 
df['hour'] = df['created_at'].dt.hour
df['minute'] = df['created_at'].dt.minute
df['time'] = df['hour'] * 60 + df['minute']
df['hour_minute'] = df['created_at'].dt.strftime('%H:%M')
df['date_str'] = df['created_at'].dt.strftime('%d %m %Y')
df['day_name'] = df['created_at'].dt.day_name()

df.sort_values(by='time', inplace=True)

res_hour_minute = df.groupby('hour_minute')['sgv'].agg([
    ('min', 'min'),
    ('max', 'max'),
    ('mean', 'mean'),
    ('25th_percentile', lambda x: x.quantile(0.25)),
    ('50th_percentile', lambda x: x.quantile(0.5)),
    ('75th_percentile', lambda x: x.quantile(0.75))
])

res_date_str = df.groupby('date_str')['sgv'].agg([
    ('min', 'min'),
    ('max', 'max'),
    ('mean', 'mean'),
    ('25th_percentile', lambda x: x.quantile(0.25)),
    ('50th_percentile', lambda x: x.quantile(0.5)),
    ('75th_percentile', lambda x: x.quantile(0.75))
])

res_hour_minute = res_hour_minute.rolling(10).mean().reset_index()

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Plot for res_hour_minute
ax1.plot(res_hour_minute['hour_minute'], res_hour_minute['min'], label='min')
ax1.plot(res_hour_minute['hour_minute'], res_hour_minute['mean'], label='mean')
ax1.plot(res_hour_minute['hour_minute'], res_hour_minute['max'], label='max')

current_ticks = ax1.get_xticks()
new_ticks = current_ticks[::60]
ax1.set_xticks(new_ticks)

ax1.set_title('SGV per Hour and Minute')
ax1.set_xlabel('Time (Hour:Minute)')
ax1.set_ylabel('SGV')
ax1.legend()
ax1.grid(True) 

############################################# Plot for res_date_str #############################################
res_date_str = res_date_str.reset_index() 

res_date_str['date_str'] = pd.to_datetime(res_date_str['date_str'], format='%d %m %Y')
res_date_str.sort_values(by='date_str', inplace=True)

ax2.plot(res_date_str['date_str'], res_date_str['mean'], label='Mean SGV per Day')



ax2.set_title('SGV per Date')
ax2.set_xlabel('Date')
ax2.set_ylabel('SGV')
ax2.legend()
ax2.grid(True) 

plt.tight_layout()
plt.show()
