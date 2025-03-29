from utils.get_readings import getReadings
from utils.glucose_analysis import GlucoseAnalysis

from utils.plot_glucose_data import plot_glucose_data

date = '2024-01-15'

# 1. 2024-01-22
# 2. 2024-01-28
# 3. 2024-01-15
# 4. 2023-10-25
# 5. 2023-03-10

# Load dataframes
gr = getReadings()

insulin_carbs = gr.get_insulin_carbs(date)
sugar_values = gr.get_sgv(date)
temp_basal = gr.get_temp_basal(date)
bolus_wizard = gr.get_bolus_wizard(date)


ga = GlucoseAnalysis(sugar_values)

for key, val in ga.calculate_summary().items():
    print(f'{key}: {val}')

plot_glucose_data(date, temp_basal, insulin_carbs, sugar_values)
