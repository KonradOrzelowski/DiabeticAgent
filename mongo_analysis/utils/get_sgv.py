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

# 2023-12-31
def get_sgv(date):
    # Connect to MongoDB
    client = MongoClient(MONGO_URI)
    db = client["diabetic_records"]

    # Get all collections in 'diabetic_records' database
    collections = db.list_collection_names()

    collection = db['Entries']

    documents = collection.find({
        'sgv': {'$exists': True},
        'dateString': {'$regex': f'^{date}'}
    })
    
    data = list(documents)

    df = pd.DataFrame(data)

    df['created_at'] = pd.to_datetime(df['dateString'])

    

    return df.sort_values(by = 'created_at')