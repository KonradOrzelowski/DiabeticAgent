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
query = {
    'durationInMilliseconds': {'$exists': True},
    'rate': {'$exists': True}
}
df = gt.get_data_from_collection(collection_name, query)

df['duration_in_hours'] = df.durationInMilliseconds / 3600000
df['insulin_given'] = df['duration_in_hours'] * df['rate'] 
############################################################################################
collection_name = 'Treatments'
gt = getReadings()
query = {
    'insulin': {'$exists': True}
}
df_insulin = gt.get_data_from_collection(collection_name, query)

############################################################################################

df_basal = process_dataframe(df, 'insulin_given')
df_injec = process_dataframe(df_insulin, 'insulin')

df_basal = df_basal.add_prefix('basal_')
df_injec = df_injec.add_prefix('injec_')


df = df_basal.join(df_injec, how='inner') 
df['total_insulin'] = df['injec_sum'] + df['basal_sum']

df_total_insulin = df.copy()

############################################################################################
collection_name = 'Treatments'
gt = getReadings()
query = {'carbs': {'$exists': True}}
df = gt.get_data_from_collection(collection_name, query)

df_carbs = process_dataframe(df, 'carbs')

############################################################################################
collection_name = 'Entries'
gt = getReadings()
query = {'sgv': {'$exists': True}}
df = gt.get_data_from_collection(collection_name, query)
df_sgv = process_dataframe(df, 'sgv')


# print(df_total_insulin.head())
# print(df_carbs.head())
# print(df_sgv.head())
############################################# heatmap  #############################################
import calplot
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

colors = ['deepskyblue', 'lawngreen', 'orangered']
cmap = LinearSegmentedColormap.from_list('bgr_custom', colors, N=256)

def plot_calendar_heatmap(df, column_name, title):
    if not isinstance(df.index, pd.DatetimeIndex):
        df = df.reset_index()

    df['date'] = pd.to_datetime(df['date_str'], format='%d %m %Y')
    df.set_index('date', inplace=True)

    values = df[column_name]

    fig, axes = calplot.calplot(
        values,
        cmap=cmap,
        colorbar=False,
        vmin=values.quantile(0.1),
        vmax=values.quantile(0.9)
    )

    fig.suptitle(title, fontsize=16)

    norm = plt.Normalize(vmin=values.quantile(0.1), vmax=values.quantile(0.9))
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])

    cbar_ax = fig.add_axes([0.92, 0.15, 0.02, 0.7])  
    cbar = fig.colorbar(sm, cax=cbar_ax)
    cbar.set_label(column_name, rotation=270, labelpad=15)

    fig.tight_layout(rect=[0, 0, 0.9, 0.95])  #



    

# Plot for total insulin
plot_calendar_heatmap(df_total_insulin, 'total_insulin', 'Total Insulin (Basal + Injection)')

# Plot for carbs
plot_calendar_heatmap(df_carbs, 'sum', 'Carbs Intake')

# Plot for glucose (sgv)
plot_calendar_heatmap(df_sgv, 'mean', 'Glucose (SGV) Mean')

plt.show()

# ############################################# plots  #############################################
# def normalize_dataframe(df, column_name):
#     if not isinstance(df.index, pd.DatetimeIndex):
#         df = df.reset_index()

#     df['date'] = pd.to_datetime(df['date_str'], format='%d %m %Y')
#     df = df.sort_values(by = 'date')
#     df.set_index('date', inplace=True)

#     values = df[column_name]

#     # values = values.clip(lower=values.quantile(0.1), upper=values.quantile(0.9))

#     # values = (values-values.min())/(values.max()-values.min())

#     return values

# v_total_insulin = normalize_dataframe(df_total_insulin, 'total_insulin')
# v_carbs = normalize_dataframe(df_carbs, 'sum')
# v_sgv = normalize_dataframe(df_sgv, 'mean')

# fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

# # Insulin subplot
# v_total_insulin.plot(ax=axs[0])
# axs[0].set_title("Total Insulin")
# axs[0].grid(True)

# # Carbs subplot
# v_carbs.plot(ax=axs[1])
# axs[1].set_title("Carbs")
# axs[1].grid(True)

# # SGV subplot
# v_sgv.plot(ax=axs[2])
# axs[2].set_title("SGV")
# axs[2].grid(True)

# plt.tight_layout()
# plt.show()
# print(v_carbs)



# import seaborn as sns



# df = pd.DataFrame([v_total_insulin, v_carbs, v_sgv]).transpose()
# print(df.head())
# # calculate the correlation matrix on the numeric columns
# corr = df.corr()

# # # plot the heatmap
# # sns.heatmap(corr)
# # plt.show()

# print(corr)