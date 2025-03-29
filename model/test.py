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
load_dotenv()

# Get MongoDB credentials from environment variables
MONGO_HOST = os.getenv("HOST_NAME")
MONGO_PORT = int(os.getenv("MONGO_PORT"))
MONGO_USER = os.getenv("MONGO_INITDB_ROOT_USERNAME")
MONGO_PASS = os.getenv("MONGO_INITDB_ROOT_PASSWORD")

# MongoDB URI
MONGO_URI = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/"


# Set OpenAI API Key
openai_api_key = os.getenv("OPENAI_API_KEY")

# Function to return measurement descriptions
def get_measurement_descriptions():
    return {
        "mean": "Average glucose level over the period.",
        "median": "Middle value of glucose readings.",
        "min": "Lowest recorded glucose level.",
        "max": "Highest recorded glucose level.",
        "q1": "First quartile (25th percentile) of glucose readings.",
        "q3": "Third quartile (75th percentile) of glucose readings.",
        "interday_cv": "Variation in glucose levels across different days.",
        "interday_sd": "Standard deviation of glucose levels across days.",
        "intraday_cv_mean": "Mean coefficient of variation within days.",
        "intraday_cv_median": "Median coefficient of variation within days.",
        "intraday_cv_sd": "Standard deviation of intraday CV values.",
        "intraday_sd_mean": "Mean standard deviation of glucose within days.",
        "intraday_sd_median": "Median standard deviation of glucose within days.",
        "intraday_sd_sd": "Standard deviation of intraday SD values.",
        "tir": "Total time (in minutes) glucose stayed in the target range.",
        "tor": "Total time (in minutes) glucose was outside the target range.",
        "pir": "Percentage of time spent in the target glucose range.",
        "por": "Percentage of time spent outside the target glucose range.",
        "mge": "Mean glucose level when outside the target range.",
        "mgn": "Mean glucose level when within the target range.",
        "gvi": "Glycemic Variability Index, indicating glucose fluctuations.",
        "pgs": "Patient Glycemic Status, a measure combining glucose level, variability, and time in range."
    }

# Create LangChain tool for measurement descriptions
measurement_tool = Tool(
    name="DescribeMeasurement",
    func=lambda _: get_measurement_descriptions(),
    description="Provides brief explanations of various glucose statistics."
)

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
llm = ChatOpenAI(model_name="gpt-3.5-turbo", api_key=openai_api_key)

agent = initialize_agent(
    tools=[measurement_tool, daily_stats],
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# Run the agent
response = agent.run("Give me the five best days and tell me why they are the best. Out of these best days, give me some insights into them. I would like to better manage my diabetes based on these five days. Ignore data from year 2022.")
print("Agent Response:", response)





