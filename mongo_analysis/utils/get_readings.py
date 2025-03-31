import os

import pandas as pd
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv
from pymongo import MongoClient

from dotenv import load_dotenv
load_dotenv()

class getReadings:
    def __init__(self, database = "diabetic_records"):

        self.database = database

        self.MONGO_HOST = os.getenv("HOST_NAME")
        self.MONGO_PORT = int(os.getenv("MONGO_PORT"))
        self.MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
        self.MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")



        self.MONGO_URI = f"mongodb://{self.MONGO_USER}:{self.MONGO_PASS}@{self.MONGO_HOST}:{self.MONGO_PORT}/"

        # Connect to MongoDB
        try:
            self.client = MongoClient(self.MONGO_URI, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.database]
        except Exception as e:
            print(f"Could not connect to MongoDB: {e}")



    def get_data_from_collection(self, collection_name, query, sort_by='created_at'):
        """
        Helper function to retrieve data from a MongoDB collection and return it as a pandas DataFrame.
        
        Parameters:
            collection_name (str): The name of the collection to query.
            query (dict): The query to execute.
            sort_by (str): The field to sort the results by (default is 'created_at').
        
        Returns:
            pd.DataFrame: A DataFrame containing the query results sorted by the specified field.
        """
        collection = self.db[collection_name]
        documents = collection.find(query).sort(sort_by, 1)  # 1 for ascending order
        data = list(documents)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)

        has_created_at = 'created_at' in df.columns
        has_dateString = 'date' in df.columns
        
        # Convert 'created_at' to datetime and sort
        if has_created_at:
            df['created_at'] = pd.to_datetime(df['created_at'])
            
        elif not has_created_at and has_dateString:
            
            df['created_at'] = pd.to_datetime(df["date"], unit="ms")

        # else:
        #     raise ValueError('No time column!')

        # df[sort_by] = df[sort_by].to_timestamp()

        df.sort_values(by=sort_by, inplace=True)

        return df


    def get_bolus_wizard(self, date):

        collection_name = 'Treatments'

        query = {
            'eventType': 'Bolus Wizard',
            'created_at': {'$regex': f'^{date}'}
        }

        return self.get_data_from_collection(collection_name, query)



    def get_insulin_carbs(self, date):

        collection_name = 'Treatments'

        query = {
            '$or': [ 
                { 'insulin': {'$exists': True} }, 
                { 'carbs': {'$exists': True} }
            ],
            'created_at': {'$regex': f'^{date}'}
        }

        return self.get_data_from_collection(collection_name, query)

    def get_sgv(self, date):

        collection_name = 'Entries'

        query = {
            'sgv': {'$exists': True},
            'dateString': {'$regex': f'^{date}'}
        }

        return self.get_data_from_collection(collection_name, query)


    def get_temp_basal(self, date):

        collection_name = 'Treatments'

        query = {
            'rate': {'$exists': True},
            'created_at': {'$regex': f'^{date}'}
        }

        return self.get_data_from_collection(collection_name, query)

    
    def get_carbs_info(self, date, time_diff = 5):
        pass