import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

def plot_glucose_data(date, temp_basal, insulin_carbs, sugar_values):
    """
    Plots basal rate over time (ax1) and glucose, insulin, and carbs (ax2 with ax3 as secondary y-axis).
    
    Parameters:
        temp_basal (pd.DataFrame): DataFrame containing 'created_at', 'rate', and 'duration' columns.
        insulin_carbs (pd.DataFrame): DataFrame containing 'created_at', 'insulin', and 'carbs' columns.
        sugar_values (pd.DataFrame): DataFrame containing 'created_at' and 'sgv' (glucose) columns.
    """
    
    fig, (ax1, ax2) = plt.subplots(2, figsize=(10, 8), sharex=True)

    plt.title(date)

    # Basal Rate on ax1
    for _, row in temp_basal.iterrows():
        start_time = row['created_at']
        rate = row['rate']
        duration = row['duration']
        end_time = start_time + pd.to_timedelta(duration, unit='m')

        ax1.fill_betweenx(
            y=[0, rate], 
            x1=start_time,  
            x2=end_time,  
            color='skyblue', 
            edgecolor='blue'
        )

    ax1.set_title('Basal Rate Over Time')
    ax1.set_ylabel('Basal Rate (units/min)')
    ax1.grid(True, axis='x', linestyle='--', alpha=0.5)

    ax3 = ax2.twinx()  

    
    ax2.plot(sugar_values.created_at, sugar_values.sgv, linestyle='-', color='blue', linewidth=2, label='Glucose')



    # Plot high, raised, and low thresholds
    start_time = sugar_values.created_at.iloc[0]
    end_time = sugar_values.created_at.iloc[-1]

    ax2.plot([start_time, end_time], [180, 180], linestyle='-', color='red', linewidth=1, label='High')
    ax2.plot([start_time, end_time], [140, 140], linestyle='-', color='orange', linewidth=1, label='Raised') 
    ax2.plot([start_time, end_time], [80, 80], linestyle='-', color='blue', linewidth=1, label='Low')
    
    ax2.grid(True, which='both', axis='both', linestyle='--', alpha=0.5)

    ax3.scatter(insulin_carbs.created_at, insulin_carbs.insulin, color='red', marker='o', label='Insulin')
    ax3.scatter(insulin_carbs.created_at, insulin_carbs.carbs, color='green', marker='s', label='Carbs')

    ax2.set_ylabel('Glucose Levels (mg/dL)', color='blue')
    ax3.set_ylabel('Insulin (units) / Carbs (g)', color='black')

    ax2.legend(loc='upper left')
    ax3.legend(loc='upper right')

    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=2))
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.show()
