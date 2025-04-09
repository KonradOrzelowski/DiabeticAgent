import numpy as np
import pandas as pd
from scipy.interpolate import interp1d
from datetime import timedelta

# Preprocessing: Interpolation to create an equidistant time grid
def preprocess_data(data, time_interval='15T'):
    """
    Interpolates the glucose data to create an equidistant time grid.
    Arguments:
        - data: DataFrame with 'timestamp' and 'glucose' columns.
        - time_interval: The desired interval between data points (e.g., '15T' for 15 minutes).
    Returns:
        - interpolated_data: DataFrame with interpolated glucose values.
    """
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data = data.set_index('timestamp').sort_index()

    # Create a time index with the specified time interval
    time_index = pd.date_range(start=data.index.min(), end=data.index.max(), freq=time_interval)
    
    # Interpolate glucose levels to the new time index
    interpolator = interp1d(data.index.astype(int), data['glucose'].values, kind='linear', fill_value="extrapolate")
    interpolated_glucose = interpolator(time_index.astype(int))

    interpolated_data = pd.DataFrame({'timestamp': time_index, 'glucose': interpolated_glucose})
    return interpolated_data

# Event Classification
def classify_events(data, hypo_threshold=70, hyper_threshold=180, duration_threshold=30):
    """
    Classifies events based on glucose levels exceeding hypo or hyperglycemia thresholds.
    Arguments:
        - data: DataFrame with 'timestamp' and 'glucose' columns.
        - hypo_threshold: Threshold for hypoglycemia.
        - hyper_threshold: Threshold for hyperglycemia.
        - duration_threshold: Minimum duration (in minutes) to consider an event.
    Returns:
        - events: List of classified events.
    """
    events = []
    start_time = None
    start_glucose = None
    event_type = None
    
    for i, row in data.iterrows():
        if row['glucose'] < hypo_threshold:  # Hypoglycemia
            event_type = 'hypo'
        elif row['glucose'] > hyper_threshold:  # Hyperglycemia
            event_type = 'hyper'
        else:
            continue
        
        # Check if an event started, if not, start a new one
        if start_time is None:
            start_time = row['timestamp']
            start_glucose = row['glucose']
        
        # If the event is continuing (same type)
        if row['glucose'] < hypo_threshold or row['glucose'] > hyper_threshold:
            duration = (row['timestamp'] - start_time).total_seconds() / 60.0
            if duration >= duration_threshold:
                events.append({
                    'event_type': event_type,
                    'start_time': start_time,
                    'end_time': row['timestamp'],
                    'duration': duration,
                    'mean_glucose': np.mean(data['glucose']),
                })
    
    return events

# Exclusive Event Labeling: Check if events are exclusive
def lv1_excl(events):
    """
    Checks if the episodes are exclusive (no overlapping levels with other episodes).
    Arguments:
        - events: List of event dictionaries.
    Returns:
        - exclusive_events: List of exclusive events.
    """
    exclusive_events = []
    for event in events:
        overlap = False
        for other_event in events:
            if event != other_event:
                # Check for overlap
                if event['start_time'] <= other_event['end_time'] and event['end_time'] >= other_event['start_time']:
                    overlap = True
                    break
        if not overlap:
            exclusive_events.append(event)
    return exclusive_events

# Summary Statistics Calculation: Compute summary statistics for each episode type
def episode_summary(events):
    """
    Computes summary statistics for each event type.
    Arguments:
        - events: List of event dictionaries.
    Returns:
        - summary_stats: Dictionary with summary statistics for each event type.
    """
    summary_stats = {
        'total_events': len(events),
        'mean_duration': np.mean([event['duration'] for event in events]),
        'mean_glucose': np.mean([event['mean_glucose'] for event in events])
    }
    return summary_stats

# Final Function: episode_calculation - Integrates all steps
def episode_calculation(data, hypo_threshold=70, hyper_threshold=180, duration_threshold=30, time_interval='15T', return_full_data=False):
    """
    Integrates all steps of preprocessing, event classification, and summary statistics.
    Arguments:
        - data: DataFrame with 'timestamp' and 'glucose' columns.
        - hypo_threshold: Threshold for hypoglycemia.
        - hyper_threshold: Threshold for hyperglycemia.
        - duration_threshold: Minimum duration for an event to be considered.
        - time_interval: Desired time interval for interpolation.
        - return_full_data: Whether to return full data with labeled events.
    Returns:
        - If return_full_data is False, returns summary statistics for the dataset.
        - If return_full_data is True, returns the data with labeled events.
    """
    # Preprocess the data (interpolation)
    interpolated_data = preprocess_data(data, time_interval)
    
    # Classify events
    events = classify_events(interpolated_data, hypo_threshold, hyper_threshold, duration_threshold)
    
    # Check for exclusive events
    exclusive_events = lv1_excl(events)
    
    # Calculate summary statistics
    summary_stats = episode_summary(exclusive_events)
    
    if return_full_data:
        # Merge events with the full dataset
        for event in exclusive_events:
            mask = (interpolated_data['timestamp'] >= event['start_time']) & (interpolated_data['timestamp'] <= event['end_time'])
            interpolated_data.loc[mask, 'event'] = event['event_type']
        return interpolated_data
    
    return summary_stats

# Example usage:
data = pd.DataFrame({
    'timestamp': ['2025-04-01 08:00', '2025-04-01 08:15', '2025-04-01 08:30', '2025-04-01 08:45', '2025-04-01 09:00'],
    'glucose': [95, 65, 190, 75, 130]
})

# Run episode calculation with desired parameters
result = episode_calculation(data, return_full_data=False)
print(result)
