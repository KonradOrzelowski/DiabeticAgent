from langchain_community.tools import Tool  # Fix import
from langchain_openai import ChatOpenAI  # Fix LLM import
from langchain.agents import initialize_agent, AgentType
import os


import pandas as pd
import os
import json
from pymongo import MongoClient
from dotenv import load_dotenv

from bson import json_util


from mongo_analysis.utils.plot_glucose_data import plot_glucose_data

# Load environment variables from .env


# Get MongoDB credentials from environment variables
MONGO_HOST = os.getenv("HOST_NAME")
MONGO_PORT = int(os.getenv("MONGO_PORT"))
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

# MongoDB URI
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/"


# Set OpenAI API Key
openai_api_key = os.getenv("OPENAI_API_KEY")

def get_daily_stats():
    client = MongoClient(MONGO_URI)
    db = client["diabetic_records"]

    collection = db['Stats']
    documents = collection.daily_stats.find({})

    data = list(documents)

    # Convert to DataFrame
    df = pd.DataFrame(data)
    return df

daily_stats = Tool(
    name="DailyStats",
    func=lambda _: get_daily_stats(),
    description="Returns a DataFrame with glucose statistics for each day."
)

from mongo_analysis.utils.get_readings import getReadings
from mongo_analysis.utils.glucose_analysis import GlucoseAnalysis

from mongo_analysis.utils.plot_glucose_data import plot_glucose_data

def get_readings_for_date(date):
    gr = getReadings()

    insulin_carbs = gr.get_insulin_carbs(date)
    sugar_values = gr.get_sgv(date)
    temp_basal = gr.get_temp_basal(date)
    bolus_wizard = gr.get_bolus_wizard(date)



    return {
        'insulin_carbs': insulin_carbs,
        'sugar_values': sugar_values,
        'temp_basal': temp_basal
    }
    
    name = "GetGlucoseData"  # Custom name for the tool
    description = "Get insulin, carbs, sugar values, and basal information for a given date."




get_readings_for_date_tool = Tool(
    name="GetGlucoseData",
    func=lambda date: get_readings_for_date(date),
    description="Get insulin, carbs, sugar values, and basal information for a given date. Pass the date as a string in the format 'YYYY-MM-DD'."
)


# Initialize the agent
llm = ChatOpenAI(model_name="gpt-4o-mini", api_key=openai_api_key)
# model_name="gpt-3.5-turbo"
# model_name="gpt-4.5-preview"

agent = initialize_agent(
    tools=[daily_stats],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    handle_parsing_errors=True,
    verbose=True
)

context = """- Mean: Average glucose level over the period.  
- Median: Middle value of glucose readings.  
- Min: Lowest recorded glucose level.  
- Max: Highest recorded glucose level.  
- Q1: First quartile (25th percentile) of glucose readings.  
- Q3: Third quartile (75th percentile) of glucose readings.  
- Interday CV: Variation in glucose levels across different days.  
- Interday SD: Standard deviation of glucose levels across days.  
- Intraday CV Mean: Mean coefficient of variation within days.  
- Intraday CV Median: Median coefficient of variation within days.  
- Intraday CV SD: Standard deviation of intraday CV values.  
- Intraday SD Mean: Mean standard deviation of glucose within days.  
- Intraday SD Median: Median standard deviation of glucose within days.  
- Intraday SD SD: Standard deviation of intraday SD values.  
- TIR: Total time (in minutes) glucose stayed in the target range.  
- TOR: Total time (in minutes) glucose was outside the target range.  
- PIR: Percentage of time spent in the target glucose range.  
- POR: Percentage of time spent outside the target glucose range.  
- MGE: Mean glucose level when outside the target range.  
- MGN: Mean glucose level when within the target range.  
"""
# - GVI: Glycemic Variability Index, indicating glucose fluctuations.  
# - PGS: Patient Glycemic Status, a measure combining glucose level, variability, and time in range.

question = "Give me the five best days and tell me why they are the best. Out of these best days, give me some insights into them."
question = "Highly effective periods of time when diabetic control was especially good."

# Run the agent
print(agent.input_keys)



response = agent.run(input = {'question': question, 'context': context})

print("Agent Response:", response)





