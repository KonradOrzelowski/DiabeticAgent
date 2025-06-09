import os
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

from pydantic import BaseModel
from typing import Optional, List
from datetime import date

from pydantic import BaseModel, Extra, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import date

class DateParams(BaseModel):
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    dates: Optional[List[date]] = None

    model_config = ConfigDict(
        extra='allow'
    )


class getReadings:
    def __init__(self, database="diabetic_records"):
        self.database = database

        self.MONGO_HOST = os.getenv("HOST_NAME")
        self.MONGO_PORT = int(os.getenv("MONGO_PORT"))
        self.MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
        self.MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

        self.MONGO_URI = f"mongodb://{self.MONGO_USER}:{self.MONGO_PASS}@{self.MONGO_HOST}:{self.MONGO_PORT}/"

        try:
            self.client = MongoClient(self.MONGO_URI, serverSelectionTimeoutMS=5000)
            self.db = self.client[self.database]
        except Exception as e:
            print(f"Could not connect to MongoDB: {e}")

    def get_data_from_collection(self, collection_name, query, sort_by='created_at'):
        collection = self.db[collection_name]
        documents = collection.find(query).sort(sort_by, 1)
        data = list(documents)
        
        df = pd.DataFrame(data)
        if df.empty:
            return df

        # Normalize dates
        if 'created_at' in df.columns:
            df['created_at'] = pd.to_datetime(df['created_at'])
        elif 'date' in df.columns:
            # 'date' might be a timestamp (ms)
            df['created_at'] = pd.to_datetime(df['date'], unit='ms').dt.tz_localize('UTC')
        elif 'dateString' in df.columns:
            df['created_at'] = pd.to_datetime(df['dateString'])

        df.sort_values(by=sort_by, inplace=True)
        return df

    def _build_date_query(self, field_name, **kwargs):
        """
        Helper to create a MongoDB date query.

        Parameters:
        - field_name: field to filter on ('created_at' or 'dateString' etc.)
        - start_date: datetime object for start date (inclusive)
        - end_date: datetime object for end date (exclusive)
        - dates: list of date strings (e.g. ['2023-06-01', '2023-06-02'])

        Returns:
        - dict query for MongoDB
        """
        params = DateParams(**kwargs)

        query = {}
        if params.dates:
            # Match any of the dates exactly using regex
            regex_list = [f"^{d.strftime('%Y-%m-%d')}" for d in params.dates]
            query['$or'] = [{field_name: {'$regex': regex}} for regex in regex_list]

            # print(query[field_name])
        elif params.start_date and params.end_date:
            # Use range query
            query[field_name] = {
                '$gte': params.start_date.strftime('%Y-%m-%d'),
                '$lt': (params.end_date + timedelta(days=1)).strftime('%Y-%m-%d')
            }
        elif params.start_date:
            # Just one date: get that full day (start to start+1 day)
            next_day = params.start_date + timedelta(days=1)
            query[field_name] = {'$gte': params.start_date.strftime('%Y-%m-%d'), '$lt': next_day.strftime('%Y-%m-%d')}
        else:
            # All data
            query = {}
        return query

    def get_bolus_wizard(self, **kwargs):
        collection_name = 'Treatments'

        query = {
                'eventType': 'Bolus Wizard',
                **self._build_date_query('created_at', **kwargs)
            }
            

        return self.get_data_from_collection(collection_name, query)

    def get_insulin_carbs(self, **kwargs):
        collection_name = 'Treatments'


        query = {
            '$or': [
                {'insulin': {'$exists': True}},
                {'carbs': {'$exists': True}}
            ],
            **self._build_date_query('created_at', **kwargs)
        }

        return self.get_data_from_collection(collection_name, query)

    def get_sgv(self, **kwargs):
        collection_name = 'Entries'

        query = {    
            'sgv': {'$exists': True},
            **self._build_date_query('dateString', **kwargs)
        }

        return self.get_data_from_collection(collection_name, query)

    def get_temp_basal(self, **kwargs):
        collection_name = 'Treatments'

        query = {
            'rate': {'$exists': True},
            **self._build_date_query('created_at', **kwargs)
        }

        return self.get_data_from_collection(collection_name, query)
