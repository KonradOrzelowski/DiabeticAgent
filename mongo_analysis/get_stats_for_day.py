from utils.get_readings import getReadings
from utils.glucose_analysis import GlucoseAnalysis

from utils.plot_glucose_data import plot_glucose_data

date = '2024-11-06'

# Agent Response: The five best days identified based on glucose control are:

# 1. 2024-11-08:
# - Optimal average glucose (112.7 mg/dL) and median (114 mg/dL).
# - Very low intraday variability (median intraday SD = 14.674).
# - High percentage within target range (PIR = 70%), minimal percentage outside (POR = 30%).
# - Narrow glucose range (72-145 mg/dL).

# 2. 2024-11-06:
# - Excellent average (111.41 mg/dL) and median glucose (114 mg/dL).
# - Very low intraday variability (median intraday SD = 18.077).
# - High PIR (69.79%) and low POR (30.21%).
# - Narrow glucose fluctuations (68-153 mg/dL).

# 3. 2024-11-07:
# - Strong mean glucose level (118.6 mg/dL) and median (115 mg/dL).
# - Low intraday variability (median intraday SD = 21.311).
# - Highest PIR of the group (71.53%), representing excellent target-range adherence.
# - Acceptable glucose range (74-180 mg/dL).

# 4. 2024-11-05:
# - Favorable mean (113.38 mg/dL) and median glucose (112 mg/dL).
# - Stable intraday control (median intraday SD = 23.605).
# - Good PIR (67.01%) and moderate POR (32.99%).
# - Overall tight glucose control (range: 63-166 mg/dL).

# 5. 2024-11-04:
# - Good average glucose (117.06 mg/dL) with median (105 mg/dL).
# - Fairly stable intraday glucose (median intraday SD = 34.673).
# - Decent PIR (68.24%) coupled with moderate POR (31.77%).
# - Slightly broader glucose range (39-204 mg/dL), still reasonable.

# Insights from these best days:
# - High adherence to target glucose ranges, demonstrating effective diabetic management.
# - Low intraday variability indicates consistency and minimal drastic fluctuations, critical for long-term positive health outcomes.
# - Regular patterns, with similar mean and median glucose levels over consecutive days, indicate predictability and likely good adherence to treatment/management routines.

# Overall, these five days represent optimal diabetes management, characterized primarily by excellent consistency, stability, and a high percentage of glucose readings within the desired target range.

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
