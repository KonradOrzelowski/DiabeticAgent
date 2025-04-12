from datetime import datetime
from pymongo import MongoClient
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from utils.get_readings import getReadings

def process_dataframe(df, column_to_agg, date_str = '09/01/2022', is_utc = True):

    df['created_at'] = pd.to_datetime(df['created_at']) 

    cutoff_date = pd.to_datetime(date_str, utc=is_utc)

    df = df[df['created_at'] >= cutoff_date].copy()

    df['hour'] = df['created_at'].dt.hour
    df['minute'] = df['created_at'].dt.minute
    df['time'] = df['hour'] * 60 + df['minute']
    df['hour_minute'] = df['created_at'].dt.strftime('%H:%M')
    df['date_str'] = df['created_at'].dt.strftime('%d %m %Y')
    df['day_name'] = df['created_at'].dt.day_name()

    df.sort_values(by='time', inplace=True)

    res_date_str = df.groupby('date_str')[column_to_agg].agg([
        ('min', 'min'),
        ('max', 'max'),
        ('mean', 'mean'),
        ('sum', 'sum'),
        ('25th_percentile', lambda x: x.quantile(0.25)),
        ('50th_percentile', lambda x: x.quantile(0.5)),
        ('75th_percentile', lambda x: x.quantile(0.75))
    ])

    return res_date_str

############################################################################################
collection_name = 'Treatments'
gt = getReadings()
query = {'carbs': {'$exists': True}}
df_carbs = gt.get_data_from_collection(collection_name, query)
df_carbs = df_carbs[['created_at', 'carbs']]
df_carbs['date_str'] = df_carbs['created_at'].dt.strftime('%d %m %Y')

############################################################################################
collection_name = 'Entries'
gt = getReadings()
query = {'sgv': {'$exists': True}}
df_sgv = gt.get_data_from_collection(collection_name, query)
df_sgv = df_sgv[['created_at', 'sgv']]
df_sgv['date_str'] = df_sgv['created_at'].dt.strftime('%d %m %Y')

import plotly.graph_objects as go
import pandas as pd
import numpy as np

start_date = '2022-07-01'
end_date = '2024-12-01'

df = df_sgv[(df_sgv['created_at'] >= start_date) & (df_sgv['created_at'] <= end_date)]
df['round_created_at'] = df['created_at'].dt.ceil('5min')

data_carbs = df_carbs[(df_carbs['created_at'] >= start_date) & (df_carbs['created_at'] <= end_date)]
data_carbs['round_created_at'] = data_carbs['created_at'].dt.ceil('5min')

data_carbs = data_carbs.set_index('round_created_at').join(df.set_index('round_created_at'), rsuffix='_sgv')


# Replace NaN values in the 'sgv' column with 140
data_carbs['sgv'].fillna(140, inplace=True)

# Create the figure
fig = go.Figure()

# Add a trace for the data
fig.add_trace(go.Scatter(x=df['created_at'], y=df['sgv'], mode='lines', name='Glucose Level'))
fig.add_trace(go.Scatter(
    x=data_carbs['created_at'], 
    y=data_carbs['sgv'], 
    mode='markers', 
    name='Carbs intake',
    marker=dict(
        color=data_carbs['carbs'], 
        size=data_carbs['carbs']/5, 
        showscale=True    
    ),
    hovertemplate=
        'Carbs: %{marker.size}<br>' + 
        'SGV: %{y}<br>' + 
        'Time: %{x}<br>' + 
        '<extra></extra>' 

))

# Add horizontal lines for 140, 180, and 80
fig.update_layout(
    shapes=[
        # Orange line at 140
        dict(
            type='line',
            x0=df['created_at'].min(),
            x1=df['created_at'].max(),
            y0=140,
            y1=140,
            line=dict(color='orange', width=2, dash='dash')
        ),
        # Red line at 180
        dict(
            type='line',
            x0=df['created_at'].min(),
            x1=df['created_at'].max(),
            y0=180,
            y1=180,
            line=dict(color='red', width=2, dash='dash')
        ),
        # Black line at 180
        dict(
            type='line',
            x0=df['created_at'].min(),
            x1=df['created_at'].max(),
            y0=250,
            y1=250,
            line=dict(color='black', width=2, dash='dash')
        ),
        # Blue line at 80
        dict(
            type='line',
            x0=df['created_at'].min(),
            x1=df['created_at'].max(),
            y0=80,
            y1=80,
            line=dict(color='blue', width=2, dash='dash')
        ),
    ]
)

fig.update_layout(
    title="Interactive Glucose Level Over Time",
    xaxis_title="Timestamp",
    yaxis_title="SGV (mg/dL)",
    xaxis=dict(
        rangeslider=dict(visible=True),  # Enable the range slider for zooming
        type="date",  # Set x-axis to be treated as dates
        tickformatstops=[
            # When zoomed out to show larger ranges, show dates (days)
            {
                'dtickrange': [None, "M1"],  # "None" means no zoom limit, "M1" is one month
                'value': "%Y-%m-%d %H:%M"  # Format for days
            },
            # When zoomed in to a smaller range, show hours
            {
                'dtickrange': ["M1", None],  # Zoom level between 1 month and 1 year
                'value': "%Y-%m-%d"  # Format for hours and minutes
            },
        ]
    ),
    showlegend=True
)


# Show the plot
fig.show()
