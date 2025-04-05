from datetime import datetime
from pymongo import MongoClient
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from utils.get_readings import getReadings

# Get data from MongoDB
collection_name = 'Entries'
gt = getReadings()
query = {'sgv': {'$exists': True}}
df = gt.get_data_from_collection(collection_name, query)

# Process time columns
df['hour'] = df['created_at'].dt.hour
df['minute'] = df['created_at'].dt.minute
df['time'] = df['hour'] * 60 + df['minute']
df['hour_minute'] = df['created_at'].dt.strftime('%H:%M')
df['day_name'] = df.created_at.dt.day_name()

df.sort_values(by='time', inplace=True)


sns.lineplot(data=df, x="hour_minute", y="sgv", estimator = lambda x: np.percentile(x, 95))

cm = sns.color_palette("Blues",9)

current_ticks = plt.gca().get_xticks()
print(len(current_ticks))
new_ticks = current_ticks[::60] 

plt.xticks(new_ticks)
plt.show()
