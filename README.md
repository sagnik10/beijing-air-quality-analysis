Beijing Air Quality Analysis (2013–2017)

A comprehensive exploratory data analysis project on multi-station air quality data from Beijing covering the period 2013–2017. This project investigates pollutant trends, seasonal variations, inter-station differences, and statistical relationships between air quality indicators using Python.

Project Overview

This project analyzes historical air quality data collected from multiple monitoring stations in Beijing to identify long-term pollution trends, compare pollution levels across stations, detect seasonal patterns, examine correlations between pollutants, and highlight extreme pollution events.

Dataset Description

The dataset consists of multiple CSV files named PRSA_Data_*.csv, each corresponding to a monitoring station. The pollutants measured include PM2.5, PM10, SO2, NO2, CO, and O3. Meteorological variables include temperature, pressure, dew point, wind speed, wind direction, and rainfall. The time period covered is 2013–2017.

Technologies Used

Python 3.x
Pandas
NumPy
Matplotlib
Seaborn

Project Structure

beijing-air-quality-analysis/
Analysis.py
PRSA_Data_*.csv
Beijing_Air_Quality_Analytical_Report.pdf
README.md
.gitignore

How to Run

Clone the repository:

git clone [https://github.com/yourusername/beijing-air-quality-analysis.git](https://github.com/yourusername/beijing-air-quality-analysis.git)
cd beijing-air-quality-analysis

Install dependencies:

pip install pandas numpy matplotlib seaborn

Run the analysis script:

python Analysis.py

Data Loading

import pandas as pd
import glob

files = glob.glob("PRSA_Data_*.csv")
df_list = [pd.read_csv(file) for file in files]
data = pd.concat(df_list, ignore_index=True)
print(data.head())

Data Cleaning

print(data.isnull().sum())
data = data.dropna(subset=["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"])

Time-Series Trend Analysis

import matplotlib.pyplot as plt

data["date"] = pd.to_datetime(data[["year", "month", "day"]])
monthly_pm25 = data.groupby(data["date"].dt.to_period("M"))["PM2.5"].mean()
monthly_pm25.plot(figsize=(12,6))
plt.title("Monthly Average PM2.5 Levels (2013–2017)")
plt.xlabel("Month")
plt.ylabel("PM2.5 Concentration")
plt.show()

Correlation Analysis

import seaborn as sns

corr_matrix = data[["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]].corr()
plt.figure(figsize=(8,6))
sns.heatmap(corr_matrix, annot=True, cmap="coolwarm")
plt.title("Correlation Between Pollutants")
plt.show()

Station-wise Comparison

station_avg = data.groupby("station")["PM2.5"].mean().sort_values()
station_avg.plot(kind="bar", figsize=(10,6))
plt.title("Average PM2.5 by Monitoring Station")
plt.ylabel("PM2.5 Concentration")
plt.show()

Key Insights

PM2.5 levels exhibit strong seasonal variation, typically peaking during winter months.
Certain stations consistently record higher pollution levels.
Strong positive correlation is observed between PM2.5 and PM10.
O3 shows different seasonal behavior compared to particulate pollutants.
Pollution levels show gradual improvement trends in later years.

Final Report

Detailed analytical findings are available in Beijing_Air_Quality_Analytical_Report.pdf.

Skills Demonstrated

Data cleaning and preprocessing
Time-series analysis
Exploratory data analysis
Data visualization
Statistical correlation analysis
Multi-dataset integration