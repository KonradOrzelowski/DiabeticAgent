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
# Load environment variables from .env
load_dotenv()

# Get MongoDB credentials from environment variables
MONGO_HOST = os.getenv("HOST_NAME")
MONGO_PORT = int(os.getenv("MONGO_PORT"))
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

# MongoDB URI
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/"


client = MongoClient(MONGO_URI)
db = client["diabetic_records"]

# Get all collections in 'diabetic_records' database
collections = db.list_collection_names()

collection = db['Treatments']

documents = collection.find({
    '$or': [ 
        { 'insulin': {'$exists': True} }, 
        { 'carbs': {'$exists': True} }
    ],
    'created_at': {'$regex': '^2023-12-31'}
})
data = list(documents)

df = pd.DataFrame(data)

df['created_at'] = pd.to_datetime(df['created_at'])


df.sort_values(by = 'created_at')

sugar_values = get_sgv('2023-12-31')
temp_basal = get_temp_basal('2023-12-31')

fig, (ax1, ax2) = plt.subplots(2)
fig.suptitle('Axes values are scaled individually by default')

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

ax2.scatter(df.created_at, df.insulin)
ax2.scatter(df.created_at, df.carbs)
ax2.plot(sugar_values.created_at, sugar_values.sgv)
plt.show()


