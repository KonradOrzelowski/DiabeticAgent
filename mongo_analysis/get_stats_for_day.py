import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import pandas as pd
from bson import json_util
import numpy as np

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from metric import calculate_gvi, calculate_pgs

from utils.get_sgv import get_sgv
from utils.get_temp_basal import get_temp_basal
from utils.get_bolus_wizard import get_bolus_wizard
from utils.get_insulin_carbs import get_insulin_carbs
# Load environment variables from .env
load_dotenv()

date = '2023-12-31'

# Load dataframes
insulin_carbs = get_insulin_carbs(date)
sugar_values = get_sgv(date)
temp_basal = get_temp_basal(date)
bolus_wizard = get_bolus_wizard(date)


gvi = calculate_gvi(sugar_values)
pgs = calculate_pgs(sugar_values)

# print(sugar_values)
print(gvi, pgs)


fig, (ax1, ax2) = plt.subplots(2)

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
# ax2.plot(time, glucose, label='Glucose Levels')
ax2.plot([sugar_values.created_at.iloc[0], sugar_values.created_at.iloc[-1]], [sugar_values.sgv.iloc[0], sugar_values.sgv.iloc[-1]], label='Ideal Line', linestyle='--')
ax2.legend()


plt.show()

df = sugar_values.copy()

df = df.sort_values(by='created_at')


time = (df['created_at'] - df['created_at'].iloc[0]).dt.total_seconds().values


print((df['created_at'] - df['created_at'].iloc[0]).dt.total_seconds()/60)


glucose = df['sgv'].values


time_diff = np.diff(time)
glucose_diff = np.diff(glucose)

segment_lengths = np.sqrt(time_diff**2 + glucose_diff**2)



# Total curve length
L = np.sum(segment_lengths)


start_time, start_glucose = time[0], glucose[0]
end_time, end_glucose =  time[-1], glucose[-1]


for i in list(zip(time, glucose, segment_lengths)):
    print(i)

