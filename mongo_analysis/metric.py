import numpy as np
import pandas as pd

def calculate_gvi(df):
    """
    Calculate the Glycemic Variability Index (GVI)
    
    Parameters:
        df (pd.DataFrame): DataFrame with 'created_at' (timestamps) and 'sgv' (glucose values)
    
    Returns:
        float: GVI value
    """

    df = df.sort_values(by='created_at')
    time = (df['created_at'] - df['created_at'].iloc[0]).dt.total_seconds().values
    glucose = df['sgv'].values


    time_diff = np.diff(time)
    glucose_diff = np.diff(glucose)

    segment_lengths = np.sqrt(time_diff**2 + glucose_diff**2)

    # Total curve length
    L = np.sum(segment_lengths)


    start_time, start_glucose = time[0], glucose[0]
    end_time, end_glucose =  time[-1], glucose[-1]

    L_ideal = np.sqrt((end_time - start_time)**2 + (end_glucose - start_glucose)**2)

    if L_ideal == 0:
        return(float('inf'))
    else:
        return(L / L_ideal)
        

def calculate_pgs(df, time_in_range_threshold=(70, 180)):
    """
    Calculate the Patient Glycemic Status (PGS)
    
    Parameters:
        df (pd.DataFrame): DataFrame with 'created_at' (timestamps) and 'sgv' (glucose values)
        time_in_range_threshold (tuple): Glucose range (low, high) for in-range percentage calculation
    
    Returns:
        float: PGS value
    """
    GVI = calculate_gvi(df)
    MG = df['sgv'].mean()  # Mean glucose
    PTIR = ((df['sgv'] >= time_in_range_threshold[0]) & (df['sgv'] <= time_in_range_threshold[1])).mean()  # Percentage time in range
    
    return GVI * MG * (1 - PTIR)

# # Example usage
# data = {
#     'created_at': pd.to_datetime(['2025-03-28 00:00:00', '2025-03-28 01:00:00', '2025-03-28 02:00:00', 
#                                   '2025-03-28 03:00:00', '2025-03-28 04:00:00', '2025-03-28 05:00:00']),
#     'sgv': [100, 105, 98, 110, 102, 108]
# }
# df = pd.DataFrame(data)

# gvi = calculate_gvi(df)
# pgs = calculate_pgs(df)

# print(f"Glycemic Variability Index (GVI): {gvi:.4f}")
# print(f"Patient Glycemic Status (PGS): {pgs:.4f}")
