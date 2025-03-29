from metric import calculate_summary
from plot_glucose_data import plot_glucose_data

from utils.get_readings import getReadings
from utils.glucose_analysis import GlucoseAnalysis


date = '2023-12-31'

# Load dataframes
gr = getReadings()


insulin_carbs = gr.get_insulin_carbs(date)
sugar_values = gr.get_sgv(date)
temp_basal = gr.get_temp_basal(date)
bolus_wizard = gr.get_bolus_wizard(date)


ga = GlucoseAnalysis(sugar_values)

for key, val in ga.calculate_summary(sugar_values).items():
    print(f'{key}: {val}')

plot_glucose_data(date, temp_basal, insulin_carbs, sugar_values)
