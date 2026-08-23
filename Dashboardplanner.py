import json


# =========================================================
# LOAD DATA PROFILE
# =========================================================

PROFILE_FILE = "data_profile.json"

with open(PROFILE_FILE, "r") as file:
    data_profile = json.load(file)


print("DATA PROFILE LOADED SUCCESSFULLY\n")

print("Dimensions:")
print(data_profile["dimensions"])

print("\nDate dimensions:")
print(data_profile["date_dimensions"])

print("\nMeasures:")
print(data_profile["measures"])


# =========================================================
# BUILD PROMPT FOR DASHBOARD PLANNER
# =========================================================

prompt = f"""
You are an expert dashboard planner.

Your job is to analyze the following dataset profile and create a dashboard plan.

DATASET PROFILE:

Dimensions:
{data_profile["dimensions"]}

Date dimensions:
{data_profile["date_dimensions"]}

Measures:
{data_profile["measures"]}

Create a meaningful dashboard using ONLY the available columns.

Decide:
1. A suitable dashboard title
2. Important KPI cards
3. Useful charts
4. Appropriate chart types
5. X-axis and Y-axis for each chart
6. Useful filters

Return the dashboard plan in JSON format only.
"""

print("\nPROMPT CREATED SUCCESSFULLY\n")
print(prompt)
