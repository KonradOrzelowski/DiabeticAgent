import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv
import pandas as pd
from bson import json_util
import numpy as np

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

from metric import calculate_summary
from plot_glucose_data import plot_glucose_data

from utils.get_sgv import get_sgv
from utils.get_temp_basal import get_temp_basal
from utils.get_bolus_wizard import get_bolus_wizard
from utils.get_insulin_carbs import get_insulin_carbs
# Load environment variables from .env
load_dotenv()

date = '2023-12-31'

# Load dataframes
insulin_carbs = get_insulin_carbs(date)
sugar_values = get_sgv(date)
temp_basal = get_temp_basal(date)
bolus_wizard = get_bolus_wizard(date)


print()

for key, val in calculate_summary(sugar_values).items():
    print(f'{key}: {val}')

plot_glucose_data(date, temp_basal, insulin_carbs, sugar_values)
