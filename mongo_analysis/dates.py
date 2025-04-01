from datetime import datetime, timedelta, timezone
from pymongo import MongoClient
import pandas as pd
# Define the date
date = '2023-12-31'

# Convert to datetime with UTC timezone
f_date = datetime.strptime(f'{date}T00:00:00', "%Y-%m-%dT%H:%M:%S")

# Calculate ±5 hours
start_time = f_date - timedelta(hours=5)
end_time = f_date + timedelta(hours=24+5)



#######################################################################################################
from utils.get_readings import getReadings

gt = getReadings()
collection_name = 'Treatments'

query = {
    '$or': [ 
        { 'insulin': {'$exists': True} }, 
        { 'carbs': {'$exists': True} }
    ],
    "created_at": {"$gte": str(start_time), "$lte": str(end_time)}
}

df = gt.get_data_from_collection(collection_name, query)

df['date'] = df.created_at.dt.strftime('%Y-%m-%d')


carbs = df[(df['date'] == date) & df['carbs'] > 0]

#######################################################################################################
# Calculate ±5 hours
# start_time = f_date - timedelta(hours=48)
# end_time = f_date + timedelta(hours=48)

collection_name = 'Entries'

start_timestamp = int(start_time.timestamp() * 1000)
end_timestamp = int(end_time.timestamp() * 1000)

query = {
    'sgv': {'$exists': True},
    "date": {"$gte": start_timestamp, "$lte": end_timestamp}
}

# print(query)
svg = gt.get_data_from_collection(collection_name, query)

#######################################################################################################
from utils.glucose_analysis import GlucoseAnalysis

for index, row in carbs.iterrows():

    past_date = row.created_at - timedelta(hours=5)
    future_date = row.created_at + timedelta(hours=5)

    is_from_past = (df.created_at >= past_date) & (df.created_at < row.created_at)
    is_from_future = (df.created_at <= future_date) & (df.created_at > row.created_at)

    is_from_past_svg = (svg.created_at >= past_date) & (svg.created_at < row.created_at)
    is_from_future_svg = (svg.created_at <= future_date) & (svg.created_at > row.created_at)


    print(
        f"Time: {row.created_at} | "
        f"Carbs: {row.carbs} | "
        f"Past Carbs: {df[is_from_past].carbs.sum()} | "
        f"Past Insulin: {df[is_from_past].insulin.sum()} | "
        f"Future Carbs: {df[is_from_future].carbs.sum()} | "
        f"Future Insulin: {df[is_from_future].insulin.sum()}"
    )
    ga = GlucoseAnalysis(svg[is_from_past_svg])
    summary_past = ga.calculate_summary()
    print('past sugar stats five hours')
    print(summary_past)

    ga = GlucoseAnalysis(svg[is_from_future_svg])
    summary_future = ga.calculate_summary()
    print('future sugar stats five hours')
    print(summary_future)



