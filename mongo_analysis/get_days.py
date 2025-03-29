import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import pandas as pd
from bson import json_util

from utils.get_readings import getReadings
from utils.glucose_analysis import GlucoseAnalysis

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
date = '2023-12-31'

client = MongoClient(MONGO_URI)
db = client["diabetic_records"]

collections = db.list_collection_names()

collection = db['Entries']

documents = collection.aggregate([
  {
    '$addFields': {
      'dateString': { '$toDate': '$dateString' }
    }
  },
  {
    '$project': {
      'dateString': '$dateString',
      'newField': {  
        '$concat': [
          {'$toString': { '$year': '$dateString' }}, '-',
          {'$cond': [
              { '$lt': [{'$month': '$dateString'}, 10] },  # If the month is less than 10
              {'$concat': ['0', {'$toString': { '$month': '$dateString' }}]},  # Add leading zero
              {'$toString': { '$month': '$dateString' }}  # Otherwise, just the month as is
            ]}, '-',
          {'$cond': [
              { '$lt': [{'$dayOfMonth': '$dateString'}, 10] },  # If the day is less than 10
              {'$concat': ['0', {'$toString': { '$dayOfMonth': '$dateString' }}]},  # Add leading zero
              {'$toString': { '$dayOfMonth': '$dateString' }}  # Otherwise, just the day as is
            ]}
        ]
      }
    }
  },
  { '$group': { '_id': "$newField" } }
])

data = list(documents)

df = pd.DataFrame(data)

df['date'] = pd.to_datetime(df['_id'])

df.sort_values(by='date', inplace=True)


# Load dataframes
gr = getReadings()

lst = []

from tqdm import tqdm

for date in tqdm(df._id.to_list(), desc="Processing dates", unit="date"):
    sugar_values = gr.get_sgv(date)

    ga = GlucoseAnalysis(sugar_values)

    lst.append({
        **{'date': date},
        **ga.calculate_summary()
    })

collection = db['Stats']
collection.daily_stats.insert_many(lst)
