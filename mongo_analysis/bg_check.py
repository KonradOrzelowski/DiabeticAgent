import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import pandas as pd
from bson import json_util

# Load environment variables from .env
load_dotenv()

# Get MongoDB credentials from environment variables
MONGO_HOST = os.getenv("HOST_NAME")
MONGO_PORT = int(os.getenv("MONGO_PORT"))
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

# MongoDB URI
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/"

def get_date(dataframe, date_column, year, month, day):
    d = dataframe[date_column].copy()

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

    collection = db['Entries']

    # Get all documents from the collection
    documents = collection.find(
        {'sgv': {'$exists': True}} 
    )
    
    data = list(documents)

    df = pd.DataFrame(data)

    df['dateString'] = pd.to_datetime(df['dateString'])
    
    date = get_date(df, 'dateString', 2023, 12, 31)

    print(date[['dateString', 'sgv']])




except Exception as e:
    print("❌ Error:", e)


