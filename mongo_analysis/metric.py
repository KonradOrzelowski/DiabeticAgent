import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from statsmodels.nonparametric.smoothers_lowess import lowess

def calculate_gvi(df):
    """Calculate the Glycemic Variability Index (GVI)."""
    df = df.sort_values(by='created_at').copy()
    df = df.dropna(subset=['sgv'])  # Handle missing values
    
    time = (df['created_at'] - df['created_at'].iloc[0]).dt.total_seconds().values
    glucose = df['sgv'].values

    time_diff = np.diff(time)
    glucose_diff = np.diff(glucose)

    if np.any(time_diff == 0):
        return np.nan  # Handle potential division by zero

    segment_lengths = np.sqrt(time_diff**2 + glucose_diff**2)
    L = np.sum(segment_lengths)

    start_time, start_glucose = time[0], glucose[0]
    end_time, end_glucose = time[-1], glucose[-1]

    L_ideal = np.sqrt((end_time - start_time)**2 + (end_glucose - start_glucose)**2)

    return np.inf if L_ideal == 0 else (L / L_ideal)

def calculate_pgs(df, time_in_range_threshold=(70, 180)):
    """Calculate the Patient Glycemic Status (PGS)."""
    gvi = calculate_gvi(df)
    mean_glucose = df['sgv'].mean()
    percent_time_in_range = ((df['sgv'] >= time_in_range_threshold[0]) & 
                             (df['sgv'] <= time_in_range_threshold[1])).mean()

    return gvi * mean_glucose * (1 - percent_time_in_range)

def calculate_interday_cv(df):
    """Computes the interday coefficient of variation of glucose."""
    mean_glucose = np.mean(df['sgv'])
    if mean_glucose == 0:
        return np.nan  # Prevent division by zero
    return (np.std(df['sgv']) / mean_glucose) * 100

def calculate_interday_sd(df):
    """Computes the interday standard deviation of glucose."""
    return np.std(df['sgv'])

def calculate_intraday_cv(df):
    """Computes the intraday coefficient of variation of glucose."""
    df_copy = df.copy()
    df_copy['day'] = df_copy['created_at'].dt.date
    intraday_cv_values = df_copy.groupby('day')['sgv'].apply(lambda x: np.std(x) / np.mean(x) * 100 if np.mean(x) != 0 else np.nan)
    
    return np.mean(intraday_cv_values), np.median(intraday_cv_values), np.std(intraday_cv_values)

def calculate_intraday_sd(df):
    """Computes the intraday standard deviation of glucose."""
    df_copy = df.copy()
    df_copy['day'] = df_copy['created_at'].dt.date
    intraday_sd_values = df_copy.groupby('day')['sgv'].std()

    return np.mean(intraday_sd_values), np.median(intraday_sd_values), np.std(intraday_sd_values)

def compute_thresholds(df, sd=1):
    """Computes upper and lower glucose thresholds for analysis."""
    mean_sgv = np.mean(df['sgv'])
    std_sgv = np.std(df['sgv'])
    return mean_sgv + sd * std_sgv, mean_sgv - sd * std_sgv

def calculate_tir(df, up, dw, sr=5):
    """Computes and returns the time in range."""
    return len(df[(df['sgv'] <= up) & (df['sgv'] >= dw)]) * sr 

def calculate_tor(df, up, dw, sr=5):
    """Computes and returns the time outside range."""
    return len(df[(df['sgv'] >= up) | (df['sgv'] <= dw)]) * sr

def calculate_por(df, total_time, tor):
    """Computes and returns the percent time outside range."""
    return (tor / total_time) * 100

def calculate_pir(df, total_time, tir):
    """Computes and returns the percent time inside range."""
    return (tir / total_time) * 100

def calculate_mge(df, up, dw):
    """Computes and returns the mean glucose outside specified range."""
    return np.mean(df[(df['sgv'] >= up) | (df['sgv'] <= dw)]['sgv'])

def calculate_mgn(df, up, dw):
    """Computes and returns the mean glucose inside specified range."""
    return np.mean(df[(df['sgv'] <= up) & (df['sgv'] >= dw)]['sgv'])

def calculate_summary(df): 
    """Computes and returns glucose summary metrics."""
    df = df.dropna(subset=['sgv'])  # Handle missing values
    up, dw = compute_thresholds(df)
    total_time = len(df) * 5  # Assuming each record represents 5 minutes

    tir = calculate_tir(df, up, dw)
    tor = calculate_tor(df, up, dw)

    intraday_cv_mean, intraday_cv_median, intraday_cv_std = calculate_intraday_cv(df)
    intraday_sd_mean, intraday_sd_median, intraday_sd_std = calculate_intraday_sd(df)

    return {
        'mean': round(df['sgv'].mean(), 3),
        'median': round(df['sgv'].median(), 3),
        'min': round(df['sgv'].min(), 3),
        'max': round(df['sgv'].max(), 3),
        'q1': round(df['sgv'].quantile(0.25), 3),
        'q3': round(df['sgv'].quantile(0.75), 3),
        'interday_cv': round(calculate_interday_cv(df), 3),
        'interday_sd': round(calculate_interday_sd(df), 3),
        'intraday_cv_mean': round(intraday_cv_mean, 3),
        'intraday_cv_median': round(intraday_cv_median, 3),
        'intraday_cv_sd': round(intraday_cv_std, 3),
        'intraday_sd_mean': round(intraday_sd_mean, 3),
        'intraday_sd_median': round(intraday_sd_median, 3),
        'intraday_sd_sd': round(intraday_sd_std, 3),
        'tir': round(tir, 3),
        'tor': round(tor, 3),
        'pir': round(calculate_pir(df, total_time, tir), 3),
        'por': round(calculate_por(df, total_time, tor), 3),
        'mge': round(calculate_mge(df, up, dw), 3),
        'mgn': round(calculate_mgn(df, up, dw), 3),
        'gvi': round(calculate_gvi(df), 3),
        'pgs': round(calculate_pgs(df), 3)
    }
