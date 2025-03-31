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

past_date = carbs.created_at.iloc[0] - timedelta(hours=5)



carbs.loc[:, "created_at"] = carbs["created_at"].dt.tz_convert(None)  # Remove timezone
svg["created_at"] = svg["created_at"].dt.tz_localize("UTC")  # Add UTC timezone
past_date = past_date.tz_localize("UTC") if past_date.tz is None else past_date  # Ensure UTC

svg.loc[:, "created_at"] = svg["created_at"].dt.tz_convert(None)  # Remove timezone
past_date = past_date.tz_convert(None)  # Remove timezone from Timestamp

print(carbs.created_at.iloc[0], carbs.created_at.dtype)
print(svg.created_at.iloc[0], svg.created_at.dtype)
print(past_date, type(past_date))


for index, row in carbs.iterrows():

    

    # Ensure carbs['created_at'] is timezone-aware in UTC
    carbs["created_at"] = carbs["created_at"].dt.tz_localize("UTC")  # Add UTC timezone if not already added

    # Ensure past_date and future_date are also timezone-aware in UTC
    past_date = past_date.tz_localize("UTC") if past_date.tz is None else past_date
    future_date = row.created_at + timedelta(hours=5)
    future_date = future_date.tz_localize("UTC") if future_date.tz is None else future_date

    # Now perform the comparisons
    is_from_past = (df.created_at >= past_date) & (df.created_at < row.created_at)
    is_from_future = (df.created_at <= future_date) & (df.created_at > row.created_at)

    # Similarly for SVG
    is_from_past_svg = (svg.created_at >= past_date) & (svg.created_at < row.created_at)
    is_from_future_svg = (svg.created_at <= future_date) & (svg.created_at > row.created_at)

    
    # ga = GlucoseAnalysis(svg[is_from_future_svg])
    # summary = ga.calculate_summary()

    print(
        f"Time: {row.created_at} | "
        f"Carbs: {row.carbs} | "
        f"Past Carbs: {df[is_from_past].carbs.sum()} | "
        f"Past Insulin: {df[is_from_past].insulin.sum()} | "
        f"Future Carbs: {df[is_from_future].carbs.sum()} | "
        f"Future Insulin: {df[is_from_future].insulin.sum()}"
    )

    # print(summary)

