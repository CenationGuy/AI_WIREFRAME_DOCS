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

    prompt = f"""
You are an expert enterprise dashboard planner.

Your job is to analyze the dataset profile below and create
a meaningful and well-organized dashboard plan.

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

Analyze the complexity and analytical scope of the dataset.

Decide whether the dashboard should contain:

- ONE sheet for simple datasets

OR

- MULTIPLE sheets for complex datasets with multiple
  meaningful areas of analysis.

Do NOT create multiple sheets unnecessarily.

Use multiple sheets only when separating the analysis
improves clarity and avoids an overcrowded dashboard.


========================================================
SHEET DESIGN RULES
========================================================

Each sheet should focus on a clear analytical purpose.

Examples include:

- Executive Overview
- Sales Performance
- Regional Analysis
- Product Analysis
- Customer Analysis
- Financial Performance
- Operational Analysis

Only create sheets that are meaningful for the available data.

Do not invent analytical areas that cannot be supported
by the dataset columns.


========================================================
FOR EACH SHEET DECIDE
========================================================

1. A suitable sheet title

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
- Avoid duplicate charts across sheets.
- Each sheet must have a clear purpose.
- Do not overcrowd a single sheet.
- Return ONLY valid JSON.
- Do not include explanations.
- Do not use markdown code blocks.


Return JSON in exactly this structure:

{{
    "dashboard_title": "Overall dashboard title",

    "sheets": [

        {{
            "sheet_number": 1,

            "title": "Sheet title",

            "purpose": "Short description of what this sheet analyzes",

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
                    "type": "line or bar or pie",
                    "x_axis": "column name",
                    "y_axis": "column name"
                }}
            ],

            "filters": [
                "column name"
            ]
        }}
    ]
}}
"""

    # =====================================================
    # CALL GEMINI
    # =====================================================

    response = llm.invoke(prompt)

    dashboard_spec_text = response.content


    # =====================================================
    # CONVERT JSON RESPONSE
    # =====================================================

    dashboard_spec = json.loads(
        dashboard_spec_text
    )


    # =====================================================
    # RETURN DASHBOARD SPEC
    # =====================================================

    return dashboard_spec
