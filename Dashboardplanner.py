import json

from langchain_google_genai import ChatGoogleGenerativeAI


# =========================================================
# CONFIGURATION
# =========================================================

PROJECT_ID = "vf-grp-gbissdbx-dev-1"

LOCATION = "us-central1"

MODEL_NAME = "gemini-2.5-flash"

PROFILE_FILE = "data_profile.json"

OUTPUT_FILE = "dashboard_spec.json"


# =========================================================
# GEMINI LLM
# =========================================================

llm = ChatGoogleGenerativeAI(
    model=MODEL_NAME,
    project=PROJECT_ID,
    location=LOCATION,
    vertexai=True,
    temperature=0
)


# =========================================================
# LOAD DATA PROFILE
# =========================================================

with open(PROFILE_FILE, "r") as file:
    data_profile = json.load(file)


print("========================================================")
print("DATA PROFILE LOADED SUCCESSFULLY")
print("========================================================")

print("\nDimensions:")
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

Your job is to analyze the dataset profile below and create a
meaningful dashboard plan.

You must use ONLY the available columns.

========================================================
DATASET PROFILE
========================================================

Dimensions:
{data_profile["dimensions"]}

Date dimensions:
{data_profile["date_dimensions"]}

Measures:
{data_profile["measures"]}


========================================================
YOUR TASK
========================================================

Create a dashboard plan.

Decide:

1. A suitable dashboard title

2. Important KPI cards

3. Useful charts

4. Appropriate chart types

5. X-axis and Y-axis for each chart

6. Useful filters


========================================================
IMPORTANT RULES
========================================================

- Use ONLY the columns provided in the dataset profile.
- Do not invent columns.
- Choose chart types appropriate for the data.
- Use date dimensions for time-based analysis when available.
- Use categorical dimensions for comparisons when appropriate.
- Use measures for numerical analysis.
- Return ONLY valid JSON.
- Do not include explanations.
- Do not use markdown code blocks.


Return JSON in exactly this structure:

{{
    "title": "Dashboard title",

    "kpis": [
        {{
            "title": "KPI name",
            "field": "column name",
            "aggregation": "sum"
        }}
    ],

    "charts": [
        {{
            "title": "Chart title",
            "type": "line or bar",
            "x_axis": "column name",
            "y_axis": "column name"
        }}
    ],

    "filters": [
        "column name"
    ]
}}
"""


print("\n========================================================")
print("PROMPT CREATED SUCCESSFULLY")
print("========================================================")


# =========================================================
# GENERATE DASHBOARD SPECIFICATION
# =========================================================

print("\nGENERATING DASHBOARD SPECIFICATION...\n")

response = llm.invoke(prompt)


# =========================================================
# GET LLM RESPONSE
# =========================================================

dashboard_spec_text = response.content


print("========================================================")
print("DASHBOARD PLAN GENERATED")
print("========================================================\n")

print(dashboard_spec_text)


# =========================================================
# CONVERT LLM RESPONSE TO JSON
# =========================================================

dashboard_spec = json.loads(dashboard_spec_text)


# =========================================================
# SAVE DASHBOARD SPECIFICATION
# =========================================================

with open(OUTPUT_FILE, "w") as file:
    json.dump(
        dashboard_spec,
        file,
        indent=4
    )


print("\n========================================================")
print("DASHBOARD SPECIFICATION GENERATED SUCCESSFULLY")
print("========================================================")

print(f"\nSaved to: {OUTPUT_FILE}")
