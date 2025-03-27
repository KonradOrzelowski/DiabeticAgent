import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import pandas as pd
from bson import json_util

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

# Load environment variables from .env
load_dotenv()

# Get MongoDB credentials from environment variables
MONGO_HOST = os.getenv("HOST_NAME")
MONGO_PORT = int(os.getenv("MONGO_PORT"))
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

# MongoDB URI
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/"

def get_date(dataframe, year, month, day):
    d = dataframe['created_at'].copy()

    is_year = d.dt.year == year
    is_month = d.dt.month == month
    is_day = d.dt.day == day

    is_date = is_year & is_month & is_day

    return dataframe[is_date]


try:
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client["diabetic_records"]

    # Get all collections in 'diabetic_records' database
    collections = db.list_collection_names()

    unique_structures = {}

    collection = db['Treatments']

    # Get all documents from the collection
    documents = collection.find({
        'rate': {'$exists': True},
        'created_at': {'$regex': '^2023-12-31'}
    })
    
    
    data = list(documents)

    df = pd.DataFrame(data)
    # Convert 'created_at' to datetime
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.sort_values(by = 'created_at')
    # Initialize the plot
    plt.figure(figsize=(10, 6))

    # Loop through each row and plot horizontal lines for each event
    for index, row in df.iterrows():
        start_time = row['created_at']
        end_time = start_time + pd.to_timedelta(row['duration'], unit='m')
        plt.hlines(y=row['rate'], xmin=start_time, xmax=end_time, color='b', linewidth=4)

    # Labeling the plot
    plt.title('Basal Insulin Rate Over Time')
    plt.xlabel('Time')
    plt.ylabel('Basal Rate (units/min)')
    plt.xticks(rotation=45)
    plt.grid(True)

    # Show plot
    plt.tight_layout()
    plt.show()
    print(df[['created_at', 'eventType', 'isValid', 'duration', 'durationInMilliseconds', 'type', 'rate', 'percent']])


except Exception as e:
    print("❌ Error:", e)


