import json

from langchain_google_genai import ChatGoogleGenerativeAI


# =========================================================
# CONFIGURATION
# =========================================================

PROJECT_ID = "vf-grp-gbissdbx-dev-1"

LOCATION = "us-central1"

MODEL_NAME = "gemini-2.5-flash"


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
# CREATE DASHBOARD PLAN
# =========================================================

def create_dashboard_plan(data_profile):

    # =====================================================
    # BUILD PROMPT
    # =====================================================

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


    # =====================================================
    # CALL GEMINI
    # =====================================================

    response = llm.invoke(prompt)

    dashboard_spec_text = response.content


    # =====================================================
    # CONVERT RESPONSE TO PYTHON DICTIONARY
    # =====================================================

    dashboard_spec = json.loads(
        dashboard_spec_text
    )


    # =====================================================
    # RETURN RESULT TO main.py
    # =====================================================

    return dashboard_spec
