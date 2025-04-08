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

    df = df[df['created_at'] >= cutoff_date]

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
query = {
    'durationInMilliseconds': {'$exists': True},
    'rate': {'$exists': True}
}
df = gt.get_data_from_collection(collection_name, query)

df['duration_in_hours'] = df.durationInMilliseconds / 3600000
df['insulin_given'] = df['duration_in_hours'] * df['rate'] 
############################################################################################
collection_name = 'Treatments'
gt = getReadings()
query = {
    'insulin': {'$exists': True}
}
df_insulin = gt.get_data_from_collection(collection_name, query)

############################################################################################

df_basal = process_dataframe(df, 'insulin_given')
df_injec = process_dataframe(df_insulin, 'insulin')

df_basal = df_basal.add_prefix('basal_')
df_injec = df_injec.add_prefix('injec_')

print(df_basal.head())
print(df_injec.head())

df = df_basal.join(df_injec, how='inner') 
df['total_insulin'] = df['injec_sum'] + df['basal_sum']



# print(df[['date_str', 'insulin_given', 'insulin']])
fig, (ax1) = plt.subplots(1, 1, figsize=(10, 8))

############################################# Plot for res_date_str #############################################
df = df.reset_index() 

df['date_str'] = pd.to_datetime(df['date_str'], format='%d %m %Y')
df.sort_values(by='date_str', inplace=True)

ax1.plot(df['date_str'], df['total_insulin'], label='Sum insulin_given per Day')



ax1.set_title('insulin_given per Date')
ax1.set_xlabel('Date')
ax1.set_ylabel('insulin_given')
ax1.legend()
ax1.grid(True) 

############################################# heatmap  #############################################
import calplot
import matplotlib.pyplot as plt

df_cal = df[['date_str', 'total_insulin']]
values = df_cal.set_index('date_str')['total_insulin']

# Create the calendar heatmap
fig, axes = calplot.calplot(
    values, 
    suptitle='Calendar Heatmap',
    cmap='bwr', 
    vmin=0, 
    vmax=df_cal['total_insulin'].max()
)

plt.tight_layout()

cbar_ax = fig.axes[-1]
cbar_ax.set_position([0.9, 0.15, 0.015, 0.7]) 

plt.show()

