import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import pandas as pd
from bson import json_util

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from utils.get_sgv import get_sgv
from utils.get_temp_basal import get_temp_basal
from utils.get_insulin_carbs import get_insulin_carbs
# Load environment variables from .env
load_dotenv()

date = '2023-03-14'

# Load dataframes
insulin_carbs = get_insulin_carbs(date)
sugar_values = get_sgv(date)
temp_basal = get_temp_basal(date)

fig, (ax1, ax2) = plt.subplots(2)
# fig.suptitle('Axes values are scaled individually by default')

for index, row in temp_basal.iterrows():
    start_time = row['created_at']
    rate = row['rate']
    duration = row['duration']
    end_time = start_time + pd.to_timedelta(duration, unit='m') 

    ax1.fill_betweenx(
        y=[0, rate], 
        x1=start_time,  
        x2=end_time,  
        color='skyblue', 
        edgecolor='blue'
    )

ax1.set_title('Event Durations Over Time (Rate vs Time)')
ax1.set_xlabel('Start Time')
ax1.set_ylabel('Basal Rate (units/min)')
ax1.grid(True, axis='x', linestyle='--', alpha=0.5)

ax2.scatter(insulin_carbs.created_at, insulin_carbs.insulin)
ax2.scatter(insulin_carbs.created_at, insulin_carbs.carbs)
ax2.plot(sugar_values.created_at, sugar_values.sgv)
plt.show()


